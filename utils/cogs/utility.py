import discord
from discord import app_commands
from discord.ext import commands
from utils.embeds import EmbedBuilder
import time

class ManageView(discord.ui.View):
    """Interactive management panel"""
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="📊 Server List", style=discord.ButtonStyle.primary, custom_id="manage_servers")
    async def show_servers(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.bot.admin_ids:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Access Denied", "Admin only"),
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            embed=EmbedBuilder.info("Server List", "Use `/list_servers` to view all servers"),
            ephemeral=True
        )
    
    @discord.ui.button(label="👥 User List", style=discord.ButtonStyle.primary, custom_id="manage_users")
    async def show_users(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.bot.admin_ids:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Access Denied", "Admin only"),
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            embed=EmbedBuilder.info("User List", "Use `/user_list` to view all users"),
            ephemeral=True
        )
    
    @discord.ui.button(label="🖥️ Nodes", style=discord.ButtonStyle.secondary, custom_id="manage_nodes")
    async def show_nodes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.bot.admin_ids:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Access Denied", "Admin only"),
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            embed=EmbedBuilder.info("Nodes", "Use `/nodes` to view all nodes"),
            ephemeral=True
        )
    
    @discord.ui.button(label="❓ Help", style=discord.ButtonStyle.success, custom_id="manage_help")
    async def show_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=EmbedBuilder.info("Help", "Use `/help` to see all available commands"),
            ephemeral=True
        )

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Ping command"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green() if latency < 100 else discord.Color.orange()
        )
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="Status", value="🟢 Online", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="help", description="Show all available commands")
    async def help_command(self, interaction: discord.Interaction):
        """Help command with all commands listed"""
        is_admin = interaction.user.id in self.bot.admin_ids
        
        embed = discord.Embed(
            title="📚 Pterodactyl Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        if is_admin:
            embed.add_field(
                name="🖥️ Server Management",
                value=(
                    "`/createserver` - Create a new server\n"
                    "`/delete_server` - Delete a server\n"
                    "`/suspend` - Suspend a server\n"
                    "`/unsuspend` - Unsuspend a server\n"
                    "`/set_resources` - Update server resources\n"
                    "`/list_servers` - List all servers\n"
                    "`/server_info` - Get server details\n"
                    "`/server_search` - Search for servers"
                ),
                inline=False
            )
            
            embed.add_field(
                name="👥 User Management",
                value=(
                    "`/user_list` - List all users\n"
                    "`/user_search` - Search for a user\n"
                    "`/delete_user` - Delete a user\n"
                    "`/change_password` - Change user password"
                ),
                inline=False
            )
            
            embed.add_field(
                name="🔧 Panel & Infrastructure",
                value=(
                    "`/nodes` - List all nodes\n"
                    "`/eggs` - List available eggs\n"
                    "`/panel_status` - Check panel status\n"
                    "`/backup_list` - List server backups\n"
                    "`/maintenance_on` - Enable maintenance mode\n"
                    "`/maintenance_off` - Disable maintenance mode"
                ),
                inline=False
            )
        
        embed.add_field(
            name="🛠️ Utility",
            value=(
                "`/ping` - Check bot latency\n"
                "`/help` - Show this help message\n"
                "`/manage` - Interactive management panel (Admin only)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📌 Important Notes",
            value=(
                "• All server actions send DMs to the affected user\n"
                "• Commands marked with 🔒 are admin-only\n"
                "• Server IDs can be found with `/list_servers`"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Panel URL: {self.bot.panel_url}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="manage", description="Interactive management panel")
    async def manage_panel(self, interaction: discord.Interaction):
        """Show interactive management panel"""
        if interaction.user.id not in self.bot.admin_ids:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Access Denied", "This command is admin-only"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🎛️ Pterodactyl Management Panel",
            description="Select an option below to manage your panel:",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="📊 Quick Stats",
            value=f"Panel: {self.bot.panel_url}\nMaintenance: {'🔴 Active' if self.bot.maintenance_mode else '🟢 Inactive'}",
            inline=False
        )
        
        embed.set_footer(text=f"Admin: {interaction.user.name}")
        
        view = ManageView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="stats", description="Show bot statistics")
    async def bot_stats(self, interaction: discord.Interaction):
        """Display bot statistics"""
        uptime = int(time.time() - self.start_time)
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="🏓 Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"<t:{int(self.start_time)}:R>", inline=True)
        embed.add_field(name="🌐 Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="🔧 Maintenance", value="🔴 Active" if self.bot.maintenance_mode else "🟢 Inactive", inline=True)
        embed.add_field(name="🖥️ Panel", value=self.bot.panel_url, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
