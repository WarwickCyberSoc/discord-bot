import discord
from discord.enums import ChannelType
from typing import Optional, Type
# import dateparser
from abc import ABC

from society_event import SocietyEvent

MODAL_TITLE = 'Create a Cybersoc Event'

class EventModalBase(ABC, discord.ui.Modal):
    def __init__(self, prefilled: Optional[SocietyEvent] = None):
        super().__init__()
        self.event = prefilled or SocietyEvent()
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Something went wrong.', ephemeral=True)
        
class ContinueView(discord.ui.View):
    def __init__(self, event: SocietyEvent, nextModal: Type[EventModalBase]):
        super().__init__(timeout=None)
        self.event = event
        self.nextModal = nextModal

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def next_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( self.nextModal(self.event) )
        await interaction.delete_original_response()

# TODO: Create a child class with title for creating and for editing. Everyone should inherit event prop and on_error handling
class EventModal1(EventModalBase, title=MODAL_TITLE):
    def __init__(self, prefilled: Optional[SocietyEvent] = None):
        super().__init__()
        self.event = prefilled or SocietyEvent()
        
        self.titleInput.default = self.event.title
        if self.event.place and self.event.place.is_digit():
            self.placeChannelInput.component.default_values = [self.event.place]
        else:
            self.placeTextInput.default = self.event.place
        self.startDateInput.default = self.event.start
        self.endDateInput.default = self.event.end
    
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
            self.event.place = self.placeChannelInput.component.values[0].id # TODO: Check if ID is what we want to store
        else:
            self.event.place = self.placeTextInput.value
        self.event.start = self.startDateInput.value
        self.event.end = self.endDateInput.value
        
        await interaction.response.send_message(
            content="Part 1 saved. Click below to continue.",
            view=ContinueView(self.event, EventModal2),
            ephemeral=True
        )

class EventModal2(EventModalBase, title=MODAL_TITLE):
    def __init__(self, event: SocietyEvent):
        super().__init__()
        self.event = event
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
            # TODO: Request Image
            pass
        else:
            await interaction.response.send_message(
                content="Part 2 saved. Click below to continue.",
                view=FinishCreationView(self.event),
                ephemeral=True)
        
        # TODO: Add preview of event announcement (use embed?), allow for edits
        
class FinishCreationView(discord.ui.View):
    def __init__(self, event: SocietyEvent):
        super().__init__(timeout=None)
        self.event = event
        
    @discord.ui.button(label="Create Event Now", style=discord.ButtonStyle.primary)
    async def create_event_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Create event logic
        await interaction.delete_original_response()
        await interaction.response.send_message('Event "{}" Created Successfully'.format(self.event.title))

    @discord.ui.button(label="Upload Image", style=discord.ButtonStyle.primary)
    async def upload_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( FileUploadModal(self.event) )
        await interaction.delete_original_response()
        
class FileUploadModal(EventModalBase, title=MODAL_TITLE):
    def __init__(self, event: SocietyEvent):
        super().__init__()
        self.event = event
        
    promotionImageInput = discord.ui.Label(
        text='Upload Image',
        component=discord.ui.FileUpload(
            required=True
        )
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        # TODO: Create event logic, check the file is actually an image
        self.event.image = self.promotionImageInput.component.values[0].url # TODO: is url what we want? prob yes
        await interaction.response.send_message(f"Event Created Successfully!")