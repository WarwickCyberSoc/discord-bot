import discord
from discord import app_commands

import logging
import logging.handlers

import sys

from event_modal import EventModal1
from env_secrets import get_secret
from bot_client import BotClient

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

intents = discord.Intents.default()
intents.message_content = True

bot = BotClient(intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    
@bot.tree.command()
async def create_event(interaction: discord.Interaction):
    await interaction.response.send_modal( EventModal1() )
    
# @bot.tree.command()
# @app_commands.describe(event_id='The base32hex ID of the event generated during its creation')
# async def edit_event(interaction: discord.Interaction, event_id: str):
#     await interaction.response.send_modal(EventModal(event_id))

# Create ()
    # Upload Promotion Material [button]
# Edit (event_id)

bot.run(token=get_secret('BOT_TOKEN'), log_handler=None, log_level=logging.DEBUG)