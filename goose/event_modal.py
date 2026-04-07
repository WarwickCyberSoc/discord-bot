import discord
from discord.enums import ChannelType
from typing import Optional, Type
from abc import ABC

from datetime_handler import parse_to_timestamp, timestamp_to_human
from env_secrets import get_secret
from society_event import SocietyEvent

MODAL_TITLE = 'Cybersoc Event Manager'

class EventModalBase(ABC, discord.ui.Modal):
    def __init__(self, event: Optional[SocietyEvent] = None):
        super().__init__()
        self.event = event or SocietyEvent()
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Something went wrong.', ephemeral=True)

class EventModal1(EventModalBase, title=MODAL_TITLE):
    def __init__(self, event: Optional[SocietyEvent] = None):
        super().__init__(event)
        self.titleInput.default = self.event.title
        if isinstance(self.event.place, int):
            self.placeChannelInput.component.default_values = [ discord.Object(self.event.place) ]
        if isinstance(self.event.place, str):
            self.placeTextInput.default = self.event.place
        if self.event.start:
            self.startDateInput.default = timestamp_to_human(self.event.start)
        if self.event.end:
            self.endDateInput.default = timestamp_to_human(self.event.end)
    
    titleInput = discord.ui.TextInput(
        label='Name',
        style=discord.TextStyle.short,
        placeholder='Pub crawl but we all pay for the Technician\'s pints',
        required=True,
        max_length=100
    )
    
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
    
    startDateInput = discord.ui.TextInput(
        label='Start Date/Time',
        style=discord.TextStyle.short,
        placeholder='Any format, I\'ll understand.',
        required=True
    )
    
    endDateInput = discord.ui.TextInput(
        label='End Date/Time',
        style=discord.TextStyle.short,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.event.title = self.titleInput.value
        if len(self.placeChannelInput.component.values) > 0:
            self.event.place = self.placeChannelInput.component.values[0].id
        else:
            self.event.place = self.placeTextInput.value
            
        try:
            self.event.start = parse_to_timestamp(self.startDateInput.value)
            if self.endDateInput.value.strip() != '':
                self.event.end = parse_to_timestamp(self.endDateInput.value)
        except ValueError as e:
            await interaction.response.send_message(
                'Error: ' + str(e) + '. Click below to continue where you left off.',
                view=ContinueView(self.event, EventModal1),
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "Part 1 saved. Click below to continue.",
            view=ContinueView(self.event, EventModal2),
            ephemeral=True
        )
        
class ContinueView(discord.ui.View):
    def __init__(self, event: SocietyEvent, nextModal: Type[EventModalBase]):
        super().__init__(timeout=None)
        self.event = event
        self.nextModal = nextModal

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def next_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( self.nextModal(self.event) )
        await interaction.delete_original_response()

class EventModal2(EventModalBase, title=MODAL_TITLE):
    def __init__(self, event: SocietyEvent):
        super().__init__(event)
        self.longTextInput.default = self.event.long_text
        self.shortTextInput.default = self.event.short_text
        
    longTextInput = discord.ui.TextInput(
        label='Announcement Text',
        style=discord.TextStyle.long,
        placeholder='Use Markdown to make it look cool',
        required=True
    )
        
    shortTextInput = discord.ui.TextInput(
        label='Short Description',
        style=discord.TextStyle.long,
        placeholder='Used for Discord\'s Event feature, Calendar, etc.',
        required=True
    )
    
    imageCheckboxInput = discord.ui.Label(
        text='Request Image?',
        description='Leave blank if you are planning on uploading an image yourself, or if no image is to be used.',
        component=discord.ui.Checkbox()
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.event.long_text = self.longTextInput.value
        self.event.short_text = self.shortTextInput.value
        
        if self.imageCheckboxInput.component.value:
            publicity_role_mention = interaction.guild.get_role(int(get_secret('PUBLICITY_ROLE_ID')))
            await interaction.response.send_message(
                content='{} is requesting an image for "{}" [{}]'
                        .format(interaction.user.mention, self.event.title, publicity_role_mention),
                view=FinishCreationView(self.event),
                ephemeral=False)
            # TODO: Create embed preview for the publicity officer to know
        else:
            await interaction.response.send_message(
                view=FinishCreationView(self.event),
                ephemeral=True)
        
        # TODO: Add preview of event announcement (use embed?), allow for edits
        
class FinishCreationView(discord.ui.View):
    def __init__(self, event: SocietyEvent):
        super().__init__(timeout=None)
        self.event = event
        
    @discord.ui.button(label="Create Now", style=discord.ButtonStyle.primary)
    async def create_event_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Create event logic
        await interaction.response.send_message('Event "{}" Created Successfully'.format(self.event.title))
        await interaction.delete_original_response()

    @discord.ui.button(label="Upload Image and Create", style=discord.ButtonStyle.primary)
    async def upload_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( FileUploadModal(self.event) )
        await interaction.delete_original_response()
        
class FileUploadModal(EventModalBase, title=MODAL_TITLE):
    def __init__(self, event: SocietyEvent):
        super().__init__(event)
        
    promotionImageInput = discord.ui.Label(
        text='Upload Image',
        component=discord.ui.FileUpload(
            required=False
        )
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # TODO: Create event logic
        if len(self.promotionImageInput.component.values) > 0:
            # TODO: Securely download if its an image of appropriate size etc
            self.event.image = self.promotionImageInput.component.values[0].url
        await interaction.response.send_message(f"Event Created Successfully!",
                                                ephemeral=True)