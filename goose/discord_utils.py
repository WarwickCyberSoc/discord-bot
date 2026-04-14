from io import BytesIO

import discord

from calendar_provider import CalendarProvider
from extended_properties import ExtendedProperties
from env_secrets import get_secret
from datetime_handler import convert_utc_to_london
from society_event import SocietyEvent

def event_embed(event : SocietyEvent, interaction: discord.Interaction) -> discord.Embed:
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
    return embed
    
async def publish_event(event: SocietyEvent, interaction: discord.Interaction, calendar: CalendarProvider):
    scheduled_event = await _do_scheduled_event(event, interaction)
    message = await _do_message(event, interaction)
    calendar_event_id = calendar.do_event(
        event,
        ExtendedProperties(scheduled_event_id=scheduled_event.id, message_id=message.id)
    )
    
    if event.id:
        await interaction.response.send_message(
            content='`{}` Edited Successfully (id: {})'.format(event.title, calendar_event_id),
            ephemeral=False
        )
        return
    
    await interaction.response.send_message(
        content='`{}` Created Successfully (id: {})'.format(event.title, calendar_event_id),
        ephemeral=False
    )
    
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
            end = convert_utc_to_london(scheduled.end_time)
        )
        
        if scheduled.entity_type == discord.EntityType.external:
            event.location = scheduled.location
        else:
            event.location = scheduled.channel_id
            
        event.image = await scheduled.cover_image.read()
        
        return event