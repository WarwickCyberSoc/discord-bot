from io import BytesIO
from typing import Optional

import discord

from calendar_provider import CalendarProvider
from extended_properties import ExtendedProperties
from env_secrets import get_secret
from datetime_handler import convert_utc_to_london
from env_secrets import get_secret
from society_event import SocietyEvent

def event_embed(event: SocietyEvent, interaction: discord.Interaction, should_ping_publicity: bool) -> tuple[discord.Embed, Optional[discord.File]]:
    time_str = f"<t:{int(event.start.timestamp())}:s>"
    if event.end:
        time_str += f" to <t:{int(event.end.timestamp())}:s>"
    location = event.location
    if not event.has_physical_location():
        location = interaction.guild.get_channel(location).mention
        
    embed = discord.Embed(title=event.title)
    embed.add_field(name="Location", value=location, inline=True)
    embed.add_field(name="Scheduled Time", value=time_str, inline=True)
    embed.add_field(name="Brief Description", value=event.short_text, inline=False)
    
    if should_ping_publicity:
        publicity_role_mention = interaction.guild.get_role(int(get_secret('PUBLICITY_ROLE'))).mention
        embed.description = '{} is requesting an image for `{}` {}'.format(interaction.user.mention, event.title, publicity_role_mention)
    
    image = None
    if event.image:
        image = discord.File(BytesIO(event.image), 'untitled.jpg')
        embed.set_image(url=f"attachment://{image.filename}")
    
    return (embed, image)
    
async def publish_event(event: SocietyEvent, interaction: discord.Interaction, calendar: CalendarProvider):
    await interaction.response.defer(thinking=True)
    scheduled_event = await _do_scheduled_event(event, interaction)
    message = await _do_message(event, interaction)
    calendar_event_id = calendar.do_event(
        event,
        ExtendedProperties(scheduled_event_id=scheduled_event.id, message_id=message.id)
    )
    
    followup = '`{}` Created Successfully (id: {})'.format(event.title, calendar_event_id)
    if event.id:
        followup = '`{}` Edited Successfully (id: {})'.format(event.title, calendar_event_id)
    
    await interaction.followup.send(followup)
    
async def _do_scheduled_event(event: SocietyEvent, interaction: discord.Interaction) -> discord.ScheduledEvent:
    scheduled_event_builder = {
        'name' : event.title,
        'description' : event.short_text,
        'start_time' : event.start,
        'privacy_level' : discord.PrivacyLevel.guild_only
    }
    
    if event.end:
        scheduled_event_builder['end_time'] = event.end
        
    if event.has_physical_location():
        scheduled_event_builder['entity_type'] = discord.EntityType.external
        scheduled_event_builder['location'] = event.location
    else:
        scheduled_event_builder['channel'] = discord.Object(event.location)
        if interaction.guild.get_channel(event.location).type == discord.ChannelType.voice:
            scheduled_event_builder['entity_type'] = discord.EntityType.voice
        elif interaction.guild.get_channel(event.location).type == discord.ChannelType.stage_voice:
            scheduled_event_builder['entity_type'] = discord.EntityType.stage_instance
    
    if event.image:
        scheduled_event_builder['image'] = event.image
    
    if event.props:
        scheduled_event = interaction.guild.get_scheduled_event(int(event.props.scheduled_event_id))
        return await scheduled_event.edit(**scheduled_event_builder)
    else:
        return await interaction.guild.create_scheduled_event(**scheduled_event_builder)

async def _do_message(event: SocietyEvent, interaction: discord.Interaction) -> discord.Message:
    channel_id = int(get_secret('EVENTS_CHANNEL'))
    channel = interaction.guild.get_channel(channel_id)
    
    if not channel or channel.type != discord.ChannelType.text:
        raise TypeError('Events channel is not valid')
    
    image = discord.File(BytesIO(event.image), 'untitled.jpg') if event.image else None

    if event.props:
        message = await channel.fetch_message(int(event.props.message_id))
        if message.content == event.long_text:
            return message
        return await message.edit(
            content=event.long_text,
            attachments=[image] if image else []
        )

    return await channel.send(
        content=event.long_text,
        file=image
    )

async def scheduled_to_soc_event(scheduled: discord.ScheduledEvent) -> SocietyEvent:
    event = SocietyEvent(
        title = scheduled.name,
        short_text = scheduled.description,
        start = convert_utc_to_london(scheduled.start_time),
    )
    
    if scheduled.end_time:
        event.end = convert_utc_to_london(scheduled.end_time)
    
    if scheduled.entity_type == discord.EntityType.external:
        event.location = scheduled.location
    else:
        event.location = scheduled.channel_id
        
    if scheduled.cover_image:
        event.image = await scheduled.cover_image.read()
    
    return event

async def get_event_from_id(interaction: discord.Interaction, event_id: str, calendar: CalendarProvider) -> Optional[SocietyEvent]:
    props = calendar.get_event(event_id)
    if not props:
        await interaction.response.send_message('`{}` is not an existing event ID'.format(event_id))
        return None
    
    # Get most attributes from Scheduled Event
    scheduled_event = interaction.guild.get_scheduled_event(int(props.scheduled_event_id))
    if not scheduled_event:
        await interaction.response.send_message('Scheduled event not found. It may have been deleted manually?'.format(event_id))
        return None
    
    # Get some attributes from calendar
    event = await scheduled_to_soc_event(scheduled_event)
    event.id = event_id
    event.props = props
    
    # Get long_text from message
    channel = interaction.guild.get_channel(int(get_secret('EVENTS_CHANNEL')))
    message = await channel.fetch_message(int(props.message_id))
    event.long_text = message.content
    
    return event

async def cancel_event(interaction: discord.Interaction, event_id: str, calendar: CalendarProvider):
    await interaction.response.defer(ephemeral=True)
    
    props = calendar.delete_event(event_id)
    if not props:
        await interaction.followup.send('`{}` is not an existing event ID'.format(event_id))
        return
        
    channel = interaction.guild.get_channel(1491824909981188126)
    message = await channel.fetch_message(int(props.message_id))
    try:
        await message.delete()
    except discord.NotFound:
        await interaction.followup.send(
            'The announcement message for `{}` appears to have been manually deleted'.format(event_id)
        )
    
    scheduled_event = interaction.guild.get_scheduled_event(int(props.scheduled_event_id))
    if not scheduled_event:
        await interaction.followup.send(
            'The scheduled event for `{}` appears to have been manually deleted'.format(event_id)
        )
        
    title = scheduled_event.name
    await scheduled_event.cancel()
    await interaction.channel.send('`{}` Deleted Successfully (id: {})'.format(title, event_id))
    await interaction.delete_original_response()