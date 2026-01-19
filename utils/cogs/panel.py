import discord
from discord import app_commands
from discord.ext import commands
from utils.api import PterodactylAPI
from utils.embeds import EmbedBuilder
from utils.checks import is_admin, not_in_maintenance
from typing import Optional

class PanelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = PterodactylAPI(bot.panel_url, bot.app_api_key, bot.client_api_key)
    
    @app_commands.command(name="nodes", description="List all panel nodes")
    @is_admin()
    async def list_nodes(self, interaction: discord.Interaction):
        """List all nodes"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_nodes()
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Failed to fetch nodes", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        nodes = result['data']['data']
        
        if not nodes:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Nodes", "No nodes configured in the panel"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🖥️ Panel Nodes",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        for node in nodes:
            attrs = node['attributes']
            status = "🟢 Online" if attrs.get('maintenance_mode') is False else "🔴 Maintenance"
            
            embed.add_field(
                name=f"{attrs['name']} (ID: {attrs['id']})",
                value=f"Status: {status}\nFQDN: `{attrs['fqdn']}`\nMemory: {attrs['memory']} MB\nDisk: {attrs['disk']} MB",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="eggs", description="List available eggs")
    @app_commands.describe(nest_id="Nest ID (default: 1 for Minecraft)")
    @is_admin()
    async def list_eggs(self, interaction: discord.Interaction, nest_id: int = 1):
        """List eggs in a nest"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_eggs(nest_id=nest_id)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Failed to fetch eggs", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        eggs = result['data']['data']
        
        if not eggs:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Eggs", f"No eggs found in nest {nest_id}"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🥚 Eggs in Nest {nest_id}",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )
        
        for egg in eggs[:15]:
            attrs = egg['attributes']
            embed.add_field(
                name=f"{attrs['name']} (ID: {attrs['id']})",
                value=f"Author: {attrs.get('author', 'Unknown')}\nDocker: `{attrs.get('docker_image', 'N/A')[:30]}...`",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="panel_status", description="Check panel API status")
    @is_admin()
    async def panel_status(self, interaction: discord.Interaction):
        """Check panel connectivity"""
        await interaction.response.defer(ephemeral=True)
        
        is_online = await self.api.test_connection()
        
        if is_online:
            embed = EmbedBuilder.success(
                "Panel Online",
                f"✅ Successfully connected to {self.bot.panel_url}"
            )
            embed.add_field(name="API Status", value="🟢 Operational", inline=True)
            embed.add_field(name="Bot Status", value="🟢 Ready", inline=True)
        else:
            embed = EmbedBuilder.error(
                "Panel Offline",
                f"❌ Failed to connect to {self.bot.panel_url}"
            )
            embed.add_field(name="API Status", value="🔴 Unreachable", inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="maintenance_on", description="Enable maintenance mode")
    @app_commands.describe(message="Custom maintenance message")
    @is_admin()
    async def maintenance_on(self, interaction: discord.Interaction, message: str = None):
        """Enable maintenance mode"""
        self.bot.maintenance_mode = True
        
        await interaction.response.send_message(
            embed=EmbedBuilder.warning(
                "Maintenance Mode Enabled",
                "Bot is now in maintenance mode. Only admins can use commands."
            ),
            ephemeral=True
        )
        
        # Log action
        log_embed = discord.Embed(
            title="🔧 Maintenance Mode Enabled",
            description=f"Enabled by {interaction.user.mention}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        if message:
            log_embed.add_field(name="Message", value=message, inline=False)
        
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="maintenance_off", description="Disable maintenance mode")
    @is_admin()
    async def maintenance_off(self, interaction: discord.Interaction):
        """Disable maintenance mode"""
        self.bot.maintenance_mode = False
        
        await interaction.response.send_message(
            embed=EmbedBuilder.success(
                "Maintenance Mode Disabled",
                "Bot is now fully operational"
            ),
            ephemeral=True
        )
        
        # Log action
        log_embed = discord.Embed(
            title="✅ Maintenance Mode Disabled",
            description=f"Disabled by {interaction.user.mention}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="backup_list", description="List backups for a server")
    @app_commands.describe(server_uuid="Server UUID")
    @is_admin()
    async def backup_list(self, interaction: discord.Interaction, server_uuid: str):
        """List server backups"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_backups(server_uuid)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Failed to fetch backups", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        backups = result['data']['data']
        
        if not backups:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Backups", "No backups found for this server"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"💾 Backups for {server_uuid[:8]}...",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for backup in backups[:10]:
            attrs = backup['attributes']
            status = "✅ Complete" if attrs.get('is_successful') else "⏳ In Progress"
            embed.add_field(
                name=f"{attrs['name']}",
                value=f"Status: {status}\nSize: {attrs.get('bytes', 0) / 1024 / 1024:.2f} MB\nCreated: <t:{int(attrs.get('created_at', 0))}:R>",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PanelCommands(bot))
