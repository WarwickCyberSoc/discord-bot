import discord
from discord.enums import ChannelType
from typing import Optional

class SocietyEvent():
    def __init__(self, title = None, long_text = None, short_text = None, start = None, end = None, place = None, image = None):
        self.title = title
        self.long_text = long_text
        self.short_text = short_text
        self.start = start
        self.end = end
        self.place = place
        self.image = image

class EventModal(discord.ui.Modal, title='Cybersoc Event'):
    def __init__(self, prefilled: Optional[SocietyEvent] = None):
        super().__init__()
        self.event = prefilled or SocietyEvent()
        
        self.titleInput.default = self.event.title
        if self.event.place and self.event.place.is_digit():
            self.placeChannelInput.component.default_values = [self.event.place]
        else:
            self.placeTextInput.default = self.event.place
        self.longTextInput.default = self.event.long_text
        self.shortTextInput.default = self.event.short_text
    
    titleInput = discord.ui.TextInput(
        label='Name',
        style=discord.TextStyle.short,
        placeholder='Pub crawl but we all pay for the Technician\'s pints',
        required=True,
        max_length=100
    )
    
    # TODO: Move this to a separate modal
    placeChannelInput = discord.ui.Label(
        text='Place (on Discord)',
        component=discord.ui.ChannelSelect(
            required=False,
            max_values=1,
            channel_types=[
                ChannelType.voice,
                ChannelType.stage_voice
            ])
    )
    
    placeTextInput = discord.ui.TextInput(
        label='Place (outside world!)',
        style=discord.TextStyle.short,
        placeholder='Kellsey\'s',
        required=False,
        max_length=100
    )
        
    longTextInput = discord.ui.TextInput(
        label='Announcement Text',
        style=discord.TextStyle.long,
        placeholder='Use Markdown to make it look cool',
        required=True,
        max_length=1000,
    )
        
    shortTextInput = discord.ui.TextInput(
        label='Short Description',
        style=discord.TextStyle.long,
        placeholder='Used for Discord\'s Event feature, Calendar, etc.',
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # embed = discord.Embed(title=f"📅 Event: {self.title_arg}", color=discord.Color.blue())
        # embed.add_field(name="Type", value=self.short_text, inline=True)
        # embed.add_field(name="Location", value=self.place, inline=True)
        # embed.add_field(name="Time", value=f"{self.start} to {self.end}", inline=False)
        # embed.add_field(name="Description", value=self.longTextInput.value, inline=False)
        
        # if self.pub_time:
        #     embed.set_footer(text=f"Scheduled for: {self.pub_time}")
        
        # if self.image:
        #     embed.set_image(url=self.image.url)

        # await interaction.response.send_message(f"Event Created Successfully!", embed=embed)
        await interaction.response.send_message(f"Event Created Successfully!")
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Something went wrong.', ephemeral=True)
