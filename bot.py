import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class PterodactylBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.panel_url = os.getenv('PANEL_URL')
        self.app_api_key = os.getenv('APP_API_KEY')
        self.client_api_key = os.getenv('CLIENT_API_KEY')
        self.admin_ids = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
        self.log_channel_id = int(os.getenv('LOG_CHANNEL_ID', '0'))
        self.maintenance_mode = False
        
    async def setup_hook(self):
        """Load all cogs"""
        cogs = ['cogs.servers', 'cogs.users', 'cogs.panel', 'cogs.utility']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        
        await self.tree.sync()
        print("✅ Commands synced")
    
    async def on_ready(self):
        print(f"✅ {self.user} is online!")
        print(f"📊 Servers: {len(self.guilds)}")
        print(f"👥 Admin IDs: {self.admin_ids}")
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Pterodactyl Panel"
            )
        )
    
    async def log_action(self, embed: discord.Embed):
        """Log actions to admin channel"""
        if self.log_channel_id:
            try:
                channel = self.get_channel(self.log_channel_id)
                if channel:
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to log action: {e}")
    
    async def send_user_dm(self, user: discord.User, embed: discord.Embed) -> bool:
        """
        Send DM to user with fallback logging
        Returns True if successful, False otherwise
        """
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            # User has DMs disabled
            await self.log_action(
                discord.Embed(
                    title="⚠️ DM Delivery Failed",
                    description=f"Could not send DM to {user.mention} ({user.id})\n**Reason:** User has DMs disabled",
                    color=discord.Color.orange()
                )
            )
            return False
        except Exception as e:
            await self.log_action(
                discord.Embed(
                    title="❌ DM Delivery Error",
                    description=f"Failed to send DM to {user.mention} ({user.id})\n**Error:** {str(e)}",
                    color=discord.Color.red()
                )
            )
            return False

def main():
    bot = PterodactylBot()
    
    if not bot.panel_url or not bot.app_api_key:
        print("❌ Missing required environment variables!")
        return
    
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()
