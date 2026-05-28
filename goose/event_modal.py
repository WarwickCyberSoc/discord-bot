import discord
from discord.enums import ChannelType

from typing import Optional, Type
from abc import ABC

from datetime_handler import parse_datetime, datetime_format
from calendar_provider import CalendarProvider
import discord_utils
from society_event import SocietyEvent

MODAL_TITLE = 'Cybersoc Event Manager'

class EventModalBase(ABC, discord.ui.Modal):
    def __init__(self, calendar: CalendarProvider, event: Optional[SocietyEvent] = None):
        super().__init__()
        self.event = event or SocietyEvent()
        self.calendar = calendar
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Something went wrong.', ephemeral=True)

    async def retry(self, interaction: discord.Interaction, error_msg: str):
        await interaction.response.send_message(
            'Error: ' + error_msg + '.\nClick below to continue where you left off.',
            view=ContinueView(self.event, self.__class__, self.calendar),
            ephemeral=True
        )

class EventModal1(EventModalBase, title=MODAL_TITLE):
    def __init__(self, calendar: CalendarProvider, event: Optional[SocietyEvent] = None):
        super().__init__(calendar, event)
        self.titleInput.default = self.event.title
        if self.event.location and not self.event.has_physical_location():
            self.placeChannelInput.component.default_values = [ discord.Object(self.event.location) ]
        else:
            self.placeTextInput.default = self.event.location
    
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

    async def on_submit(self, interaction: discord.Interaction):
        self.event.title = self.titleInput.value
        if len(self.placeChannelInput.component.values) > 0:
            self.event.location = self.placeChannelInput.component.values[0].id
        elif self.placeTextInput.value.strip() != '':
            self.event.location = self.placeTextInput.value
        else:
            await self.retry(interaction, 'No place specified')
            return
        
        await interaction.response.send_message(
            "Part 1 saved. Click below to continue.",
            view=ContinueView(self.event, EventModal2, self.calendar),
            ephemeral=True
        )
        
class ContinueView(discord.ui.View):
    def __init__(self, event: Optional[SocietyEvent], nextModal: Type[EventModalBase], calendar: CalendarProvider):
        super().__init__(timeout=None)
        self.calendar = calendar
        self.event = event
        self.nextModal = nextModal

    @discord.ui.button(label="Continue", style=discord.ButtonStyle.primary)
    async def next_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( self.nextModal(self.calendar, self.event) )
        await interaction.delete_original_response()

class EventModal2(EventModalBase, title=MODAL_TITLE):
    def __init__(self, calendar: CalendarProvider, event: SocietyEvent):
        super().__init__(calendar, event)
        if self.event.start:
            self.startDateInput.default = datetime_format(self.event.start)
        if self.event.end:
            self.endDateInput.default = datetime_format(self.event.end)
        if self.event.has_physical_location():
            # Due to Discord API rules
            self.endDateInput.required = True
            self.endDateInput.placeholder = 'Required for grass-touching events'
        self.longTextInput.default = self.event.long_text
        self.shortTextInput.default = self.event.short_text
        self.imageCheckboxInput.component.default = self.event.is_requesting_image
        
    longTextInput = discord.ui.TextInput(
        label='Announcement Text',
        style=discord.TextStyle.long,
        placeholder='Use Markdown to make it look cool',
        required=True
    )
        
    shortTextInput = discord.ui.TextInput(
        label='Short Description (max. 1000 characters)',
        style=discord.TextStyle.long,
        placeholder='Used for Discord\'s Event feature, Calendar, etc.',
        required=True,
        max_length=1000
    )
    
    imageCheckboxInput = discord.ui.Label(
        text='Request Image?',
        description='Leave blank if you are planning on uploading an image yourself, or if no image is to be used.',
        component=discord.ui.Checkbox()
    )
    
    startDateInput = discord.ui.TextInput(
        label='Start Date/Time (defaults to UK time)',
        style=discord.TextStyle.short,
        placeholder='E.g. 01/01/1337 but natural language works as well :D',
        required=True
    )
    
    endDateInput = discord.ui.TextInput(
        label='End Date/Time (defaults to UK time)',
        style=discord.TextStyle.short,
        placeholder='If left blank, same day at 11:59PM',
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.event.long_text = self.longTextInput.value
        self.event.short_text = self.shortTextInput.value
        self.event.is_requesting_image = self.imageCheckboxInput.component.value
        
        try:
            self.event.start = parse_datetime(self.startDateInput.value)
            if self.endDateInput and self.endDateInput.value.strip() != '':
                self.event.end = parse_datetime(self.endDateInput.value)
                if self.event.start >= self.event.end:
                    raise ValueError('Cannot schedule event to end before starting')
        except ValueError as e:
            await self.retry(interaction, str(e))
            return
        
        embed, image = discord_utils.event_embed(self.event, interaction, self.imageCheckboxInput.component.value)
        attachments = [image] if image else []
        
        await interaction.response.send_message(
            content=self.event.long_text,
            view=FinishCreationView(self.calendar, self.event, interaction),
            embed=embed,
            files=attachments,
            ephemeral=not self.imageCheckboxInput.component.value)
        
class FinishCreationView(discord.ui.View):
    def __init__(self, calendar: CalendarProvider, event: SocietyEvent, callerContext: discord.Interaction):
        super().__init__(timeout=None)
        self.event = event
        self.calendar = calendar
        self.callerContext = callerContext
        
    @discord.ui.button(label="Post Now", style=discord.ButtonStyle.primary)
    async def create_event_now(self, interaction: discord.Interaction, button: discord.ui.Button):
        await discord_utils.publish_event(self.event, interaction, self.calendar)
        await self.callerContext.delete_original_response()

    @discord.ui.button(label="Upload Image and Post", style=discord.ButtonStyle.primary)
    async def upload_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( FileUploadModal(self.calendar, self.event, interaction) )
        
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary)
    async def edit_event(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal( EventModal1(self.calendar, self.event) )        

class FileUploadModal(EventModalBase, title=MODAL_TITLE):
    def __init__(self, calendar: CalendarProvider, event: SocietyEvent, callerContext: discord.Interaction):
        super().__init__(calendar, event)
        self.callerContext = callerContext
        
    promotionImageInput = discord.ui.Label(
        text='Upload Image',
        component=discord.ui.FileUpload(
            required=False
        )
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        accepted_types = [ 'image/png', 'image/jpeg', 'image/webp' ]
        if len(self.promotionImageInput.component.values) > 0:
            image = self.promotionImageInput.component.values[0]
            if image.content_type not in accepted_types:
                await self.retry(interaction, 'Image must be in one of the following formats: PNG, JPEG, or WEBP')
                return
            self.event.image = await image.read()
            
        await discord_utils.publish_event(self.event, interaction, self.calendar)
        await self.callerContext.delete_original_response()
        
class SelectEventModal(EventModalBase, title=MODAL_TITLE):
    def __init__(self, calendar: CalendarProvider, events: dict[str, str], to_delete: bool):
        super().__init__(calendar, None)
        self.to_delete = to_delete
        
        if to_delete:
            self.selectEventInput.text += 'delete'
        else:
            self.selectEventInput.text += 'edit'
        
        # len(events) >= 2
        for id, name in events.items():
            self.selectEventInput.component.add_option(
                label=name,
                value=id
            )
    
    selectEventInput = discord.ui.Label(
        text='Select the event to ',
        component=discord.ui.RadioGroup(
            required=True
        )
    )

    async def on_submit(self, interaction: discord.Interaction):
        event_id = self.selectEventInput.component.value
        
        if self.to_delete:
            await discord_utils.cancel_event(interaction, event_id, self.calendar)
            return
            
        event = await discord_utils.get_event_from_id(interaction, event_id, self.calendar)
        await interaction.response.send_message(
            "Event `{}` selected. Click below to continue.".format(event.title),
            view=ContinueView(event, EventModal1, self.calendar),
            ephemeral=True
        )