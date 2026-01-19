import discord
from discord import app_commands
from typing import Callable

def is_admin():
    """Check if user is in admin list"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id not in interaction.client.admin_ids:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Access Denied",
                    description="You don't have permission to use this command.\nOnly administrators can perform this action.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

def not_in_maintenance():
    """Check if bot is not in maintenance mode"""
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.client.maintenance_mode and interaction.user.id not in interaction.client.admin_ids:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔧 Maintenance Mode",
                    description="The bot is currently undergoing maintenance. Please try again later.",
                    color=discord.Color.orange()
                ),
                ephemeral=True
            )
            return False
        return True
    return app_commands.check(predicate)

class ConfirmView(discord.ui.View):
    """Confirmation view for destructive actions"""
    def __init__(self, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.value = None
    
    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Cancelled",
                description="Operation cancelled.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
