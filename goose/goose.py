import discord
from discord import app_commands

import logging
import logging.handlers

import sys

from env_secrets import get_secret
from bot_client import BotClient
from calendar_provider import GoogleCalendar
from event_modal import EventModal1, SelectEventModal
import discord_utils

file_handler = logging.handlers.RotatingFileHandler(
    filename='bot.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,
    backupCount=3,
)
date_format = '%Y-%m-%d %H:%M:%S'
file_format = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', date_format, style='{')
file_handler.setFormatter(file_format)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

bot = BotClient()
calendar = GoogleCalendar(get_secret('CALENDAR_ID'))

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    calendar.authenticate()

@bot.tree.command()
async def create_event(interaction: discord.Interaction):
    await interaction.response.send_modal( EventModal1(calendar) )
    
async def edit_event(interaction: discord.Interaction, event_id: str):
    event = await discord_utils.get_event_from_id(interaction, event_id, calendar)    
    await interaction.response.send_modal( EventModal1(calendar, event) )
    
@bot.tree.command(name='edit_event')
@app_commands.describe(event_id='The base32hex ID of the event')
async def edit_event_cli(interaction: discord.Interaction, event_id: str):
    await edit_event(interaction, event_id)
    
@bot.tree.command(description='Edit one of the 10 latest events from a GUI')
@app_commands.describe()
async def edit_event_gui(interaction: discord.Interaction):
    upcoming_events = calendar.get_events(10) # 10 is the Max for RadioGroup
    
    if len(upcoming_events) == 0:
        await interaction.response.send_message('There are no upcoming events.', ephemeral=True)
        return
    
    if len(upcoming_events) == 1:
        await edit_event(interaction, upcoming_events.popitem()[0])
        return
    
    await interaction.response.send_modal( SelectEventModal(calendar, upcoming_events, to_delete=False) )

@bot.tree.command(name='cancel_event')
@app_commands.describe(event_id='The base32hex ID of the event')
async def cancel_event_cli(interaction: discord.Interaction, event_id: str):
    await discord_utils.cancel_event(interaction, event_id, calendar)

@bot.tree.command(description='Cancel one of the 10 latest events from a GUI')
@app_commands.describe()
async def cancel_event_gui(interaction: discord.Interaction):
    upcoming_events = calendar.get_events(10) # 10 is the Max for RadioGroup
    
    if len(upcoming_events) == 0:
        await interaction.response.send_message('There are no upcoming events.', ephemeral=True)
        return
    
    if len(upcoming_events) == 1:
        await discord_utils.cancel_event(interaction, upcoming_events.popitem()[0], calendar)
        return
    
    await interaction.response.send_modal( SelectEventModal(calendar, upcoming_events, to_delete=True) )

bot.run(token=get_secret('BOT_TOKEN'), log_handler=None, log_level=logging.DEBUG)