import discord
from discord import app_commands
import env_secrets

class BotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        context = app_commands.AppCommandContext(guild=True)
        self.tree = app_commands.CommandTree(client=self, allowed_contexts=context)

    async def setup_hook(self):
        # This copies the global commands over to specific guild for testing (rather than wait an hour or so for Discord to catch up)
        try:
            guild_id = env_secrets.get_secret('GUILD')
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        except env_secrets.MissingSecretError:
            return # This secret is only needed for debugging