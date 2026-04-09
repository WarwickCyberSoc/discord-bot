from datetime import datetime
from typing import Optional, Union

import discord

from env_secrets import get_secret

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
        
    async def publish(self, interaction: discord.Interaction):
        # Create Scheduled Event
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
        
        scheduled_event = await interaction.guild.create_scheduled_event(**scheduled_event)
        
        # 2. Send message in [#events]
        channel_id = int(get_secret('EVENTS_CHANNEL'))
        channel = interaction.guild.get_channel(channel_id)
        
        if not channel or channel.type != discord.ChannelType.text:
            raise TypeError('Events channel is not valid')
        
        if self.image:
            message = await channel.send(content=self.long_text, file=await self.image.to_file())
        else:
            message = await channel.send(self.long_text)
        
        # TODO Create Google Calendar
        
        
        await interaction.response.send_message('{} Created Successfully ({})'.format(self.title, scheduled_event.id))