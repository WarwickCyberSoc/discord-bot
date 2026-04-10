from datetime import datetime
from typing import Optional, Union

import discord
import dismoji

from env_secrets import get_secret
from calendar_provider import CalendarProvider

class SocietyEvent():
    def __init__(self, title : Optional[str] = None, long_text : Optional[str] = None,
                 short_text : Optional[str] = None, start : Optional[datetime] = None,
                 end : Optional[datetime] = None, location : Optional[Union[str, int]] = None,
                 image : Optional[discord.Attachment] = None, is_requesting_image : bool = False):
        self.title = title
        self.location = location
        self.start = start
        self.end = end
        self.long_text = long_text
        self.short_text = short_text
        self.image = image
        self.is_requesting_image = is_requesting_image
    
    def has_physical_location(self) -> bool:
        return isinstance(self.location, str)
    
    def to_embed(self, interaction: discord.Interaction):
        time_str = f"<t:{int(self.start.timestamp())}:s>"
        if self.end:
            time_str += f" to <t:{int(self.end.timestamp())}:s>"
        location = self.location
        if not self.has_physical_location():
            location = interaction.guild.get_channel(location).mention
            
        embed = discord.Embed(title=self.title)
        embed.add_field(name="Location", value=location, inline=True)
        embed.add_field(name="Scheduled Time", value=time_str, inline=True)
        embed.add_field(name="Brief Description", value=self.short_text, inline=False)
        return embed
        
    async def publish(self, interaction: discord.Interaction, calendar: CalendarProvider):
        scheduled_event = await self._create_scheduled_event(interaction)
        message = await self._send_message(interaction)
        calendar_event_id = self._create_calendar_event(calendar, scheduled_event.id, message.id)
        sanitized_title = '`{}`'.format(self.title)
        await interaction.response.send_message(
            content='{} Created Successfully ({})'.format(sanitized_title, calendar_event_id),
            ephemeral=False
        )
        
    async def _create_scheduled_event(self, interaction: discord.Interaction) -> discord.ScheduledEvent:
        scheduled_event = {
            'name' : self.title,
            'description' : self.short_text,
            'start_time' : self.start,
            'privacy_level' : discord.PrivacyLevel.guild_only
        }
        
        if self.end:
            scheduled_event['end_time'] = self.end
            
        if self.has_physical_location():
            scheduled_event['entity_type'] = discord.EntityType.external
            scheduled_event['location'] = self.location
        else:
            scheduled_event['channel'] = discord.Object(self.location)
            if interaction.guild.get_channel(self.location).type == discord.ChannelType.voice:
                scheduled_event['entity_type'] = discord.EntityType.voice
            elif interaction.guild.get_channel(self.location).type == discord.ChannelType.stage_voice:
                scheduled_event['entity_type'] = discord.EntityType.stage_instance
        
        if self.image:
            scheduled_event['image'] = await self.image.read()
        
        return await interaction.guild.create_scheduled_event(**scheduled_event)
    
    async def _send_message(self, interaction: discord.Interaction) -> discord.Message:
        channel_id = int(get_secret('EVENTS_CHANNEL'))
        channel = interaction.guild.get_channel(channel_id)
        
        if not channel or channel.type != discord.ChannelType.text:
            raise TypeError('Events channel is not valid')
        
        if self.image:
            return await channel.send(content=self.long_text, file=await self.image.to_file())
        else:
            return await channel.send(self.long_text)
        
    def _create_calendar_event(self, calendar: CalendarProvider, scheduled_event_id: int, message_id: int) -> str:
        event = {
            'summary': dismoji.demojize(self.title),
            'location': dismoji.demojize(self.location),
            'description': dismoji.demojize(self.short_text),
            'start': self._google_datetime(self.start),
            'extendedProperties': {
                'private': {
                    'scheduled_event': scheduled_event_id,
                    'message': message_id
                }
            }
        }
        
        if not self.has_physical_location():
            event['location'] = 'Discord Server'
            
        if self.end:
            event['end'] = self._google_datetime(self.end)
        else:
            event['end'] = self._google_datetime(self.start.replace(hour=23, minute=59))
        
        return calendar.create_event(event)
            
    def _google_datetime(self, dt: datetime):
        return {
            'dateTime': dt.isoformat(timespec='seconds'),
            'timeZone': 'Europe/London'
        }