import discord
from discord import app_commands
from discord.ext import commands
from utils.api import PterodactylAPI
from utils.embeds import EmbedBuilder
from utils.checks import is_admin, not_in_maintenance, ConfirmView
import random
import string

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = PterodactylAPI(bot.panel_url, bot.app_api_key, bot.client_api_key)
    
    @app_commands.command(name="user_list", description="List all Pterodactyl users")
    @app_commands.describe(page="Page number")
    @is_admin()
    async def user_list(self, interaction: discord.Interaction, page: int = 1):
        """List all users"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_users(page=page)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Failed to fetch users", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        users = result['data']['data']
        
        if not users:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Users", "No users found on this page"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"👥 Panel Users (Page {page})",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for user in users[:10]:
            attrs = user['attributes']
            role = "👑 Admin" if attrs.get('root_admin') else "👤 User"
            embed.add_field(
                name=f"{attrs['username']} (ID: {attrs['id']})",
                value=f"{role}\nEmail: {attrs['email']}\n2FA: {'✅' if attrs.get('2fa') else '❌'}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="user_search", description="Search for a user by email or username")
    @app_commands.describe(query="Email or username to search for")
    @is_admin()
    async def user_search(self, interaction: discord.Interaction, query: str):
        """Search for users"""
        await interaction.response.defer(ephemeral=True)
        
        # Try email search first
        user = await self.api.get_user_by_email(query)
        
        if user:
            attrs = user['attributes']
            embed = discord.Embed(
                title=f"👤 User Found: {attrs['username']}",
                color=discord.Color.green()
            )
            embed.add_field(name="🆔 ID", value=attrs['id'], inline=True)
            embed.add_field(name="📧 Email", value=attrs['email'], inline=True)
            embed.add_field(name="👤 Name", value=f"{attrs['first_name']} {attrs['last_name']}", inline=True)
            embed.add_field(name="👑 Admin", value="✅" if attrs.get('root_admin') else "❌", inline=True)
            embed.add_field(name="🔐 2FA", value="✅" if attrs.get('2fa') else "❌", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Results", f"No user found with email/username: {query}"),
                ephemeral=True
            )
    
    @app_commands.command(name="delete_user", description="Delete a Pterodactyl user")
    @app_commands.describe(user_id="User ID to delete")
    @is_admin()
    @not_in_maintenance()
    async def delete_user(self, interaction: discord.Interaction, user_id: int):
        """Delete a user with confirmation"""
        # Confirmation
        view = ConfirmView()
        await interaction.response.send_message(
            embed=EmbedBuilder.warning(
                "Confirm User Deletion",
                f"Are you sure you want to delete user ID {user_id}?\n\n⚠️ This will also delete all their servers!"
            ),
            view=view,
            ephemeral=True
        )
        
        await view.wait()
        
        if not view.value:
            return
        
        # Delete user
        result = await self.api.delete_user(user_id)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Deletion Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            embed=EmbedBuilder.success(
                "User Deleted",
                f"User ID {user_id} and all associated servers have been deleted"
            ),
            ephemeral=True
        )
        
        # Log action
        log_embed = discord.Embed(
            title="🗑️ User Deleted",
            description=f"User ID {user_id} deleted by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="change_password", description="Change a user's password")
    @app_commands.describe(
        user_id="User ID",
        new_password="New password (leave empty for random)"
    )
    @is_admin()
    @not_in_maintenance()
    async def change_password(
        self,
        interaction: discord.Interaction,
        user_id: int,
        new_password: str = None
    ):
        """Change user password"""
        await interaction.response.defer(ephemeral=True)
        
        if not new_password:
            new_password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=16))
        
        result = await self.api.update_user_password(user_id, new_password)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Password Change Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        embed = EmbedBuilder.success(
            "Password Changed",
            f"Password for user ID {user_id} has been updated"
        )
        embed.add_field(name="🔑 New Password", value=f"||{new_password}||", inline=False)
        embed.add_field(name="⚠️ Important", value="Save this password securely. It won't be shown again.", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log action
        log_embed = discord.Embed(
            title="🔑 Password Changed",
            description=f"Password changed for user ID {user_id} by {interaction.user.mention}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        await self.bot.log_action(log_embed)

async def setup(bot):
    await bot.add_cog(UserCommands(bot))
