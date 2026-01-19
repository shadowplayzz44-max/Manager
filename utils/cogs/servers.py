import discord
from discord import app_commands
from discord.ext import commands
from utils.api import PterodactylAPI
from utils.embeds import EmbedBuilder
from utils.checks import is_admin, not_in_maintenance, ConfirmView
from typing import Optional

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = PterodactylAPI(bot.panel_url, bot.app_api_key, bot.client_api_key)
    
    @app_commands.command(name="createserver", description="Create a new server for a user")
    @app_commands.describe(
        name="Server name",
        ram="RAM in MB",
        cpu="CPU percentage",
        disk="Disk space in MB",
        version="Server version/type",
        node_id="Node ID",
        egg_id="Egg ID",
        user="Discord user to assign server to"
    )
    @is_admin()
    @not_in_maintenance()
    async def create_server(
        self,
        interaction: discord.Interaction,
        name: str,
        ram: int,
        cpu: int,
        disk: int,
        version: str,
        node_id: int,
        egg_id: int,
        user: discord.User
    ):
        """Create a new Pterodactyl server"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate resources
            if ram < 512 or ram > 32768:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Invalid RAM", "RAM must be between 512 MB and 32768 MB"),
                    ephemeral=True
                )
                return
            
            if cpu < 50 or cpu > 400:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Invalid CPU", "CPU must be between 50% and 400%"),
                    ephemeral=True
                )
                return
            
            if disk < 1024 or disk > 102400:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Invalid Disk", "Disk must be between 1024 MB and 102400 MB"),
                    ephemeral=True
                )
                return
            
            # Validate node
            node_check = await self.api.get_node(node_id)
            if not node_check['success']:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Invalid Node", f"Node ID {node_id} does not exist"),
                    ephemeral=True
                )
                return
            
            node_name = node_check['data']['attributes']['name']
            
            # Validate egg
            egg_check = await self.api.get_egg(egg_id)
            if not egg_check['success']:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Invalid Egg", f"Egg ID {egg_id} does not exist"),
                    ephemeral=True
                )
                return
            
            # Create or get user
            email = f"{user.name}@discord.local"
            username = user.name.lower().replace(" ", "_")
            
            pterodactyl_user = await self.api.get_user_by_email(email)
            new_user = False
            password = None
            
            if not pterodactyl_user:
                user_result = await self.api.create_user(
                    email=email,
                    username=username,
                    first_name=user.name,
                    last_name="Discord"
                )
                
                if not user_result['success']:
                    await interaction.followup.send(
                        embed=EmbedBuilder.error("User Creation Failed", user_result.get('error', 'Unknown error')),
                        ephemeral=True
                    )
                    return
                
                pterodactyl_user = user_result['data']['attributes']
                password = user_result.get('password')
                new_user = True
            
            ptero_user_id = pterodactyl_user['id']
            
            # Create server
            server_result = await self.api.create_server(
                user_id=ptero_user_id,
                name=name,
                ram=ram,
                cpu=cpu,
                disk=disk,
                node_id=node_id,
                egg_id=egg_id
            )
            
            if not server_result['success']:
                await interaction.followup.send(
                    embed=EmbedBuilder.error("Server Creation Failed", server_result.get('error', 'Unknown error')),
                    ephemeral=True
                )
                return
            
            server_data = server_result['data']['attributes']
            server_id = server_data['id']
            
            # Send success to admin
            await interaction.followup.send(
                embed=EmbedBuilder.success(
                    "Server Created",
                    f"Server **{name}** has been created for {user.mention}",
                    **{
                        "Server ID": str(server_id),
                        "Node": node_name,
                        "RAM": f"{ram} MB",
                        "CPU": f"{cpu}%",
                        "Disk": f"{disk} MB"
                    }
                ),
                ephemeral=True
            )
            
            # ========== MANDATORY DM TO USER ==========
            dm_embed = EmbedBuilder.dm_server_created(
                server_name=name,
                server_id=str(server_id),
                node=node_name,
                ram=ram,
                cpu=cpu,
                disk=disk,
                version=version,
                panel_url=self.bot.panel_url,
                username=username,
                password=password if new_user else None
            )
            
            dm_success = await self.bot.send_user_dm(user, dm_embed)
            
            # Log action
            log_embed = EmbedBuilder.log_server_action(
                action="created",
                admin=interaction.user.mention,
                user=user.mention,
                server_info={
                    'id': server_id,
                    'name': name,
                    'resources': {'ram': ram, 'cpu': cpu, 'disk': disk}
                }
            )
            
            if not dm_success:
                log_embed.add_field(
                    name="⚠️ DM Status",
                    value="Failed to send DM to user",
                    inline=False
                )
            
            await self.bot.log_action(log_embed)
            
        except Exception as e:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Error", f"An unexpected error occurred: {str(e)}"),
                ephemeral=True
            )
    
    @app_commands.command(name="delete_server", description="Delete a server")
    @app_commands.describe(
        server_id="Server ID to delete",
        user="User who owns the server"
    )
    @is_admin()
    @not_in_maintenance()
    async def delete_server(
        self,
        interaction: discord.Interaction,
        server_id: int,
        user: discord.User
    ):
        """Delete a server with confirmation"""
        # Get server info first
        server_info = await self.api.get_server(server_id)
        if not server_info['success']:
            await interaction.response.send_message(
                embed=EmbedBuilder.error("Server Not Found", f"Server ID {server_id} does not exist"),
                ephemeral=True
            )
            return
        
        server_name = server_info['data']['attributes']['name']
        
        # Confirmation
        view = ConfirmView()
        await interaction.response.send_message(
            embed=EmbedBuilder.warning(
                "Confirm Deletion",
                f"Are you sure you want to delete **{server_name}** (ID: {server_id})?\n\n⚠️ This action is irreversible!"
            ),
            view=view,
            ephemeral=True
        )
        
        await view.wait()
        
        if not view.value:
            return
        
        # Delete server
        result = await self.api.delete_server(server_id, force=True)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Deletion Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        # Success message to admin
        await interaction.followup.send(
            embed=EmbedBuilder.success(
                "Server Deleted",
                f"Server **{server_name}** (ID: {server_id}) has been permanently deleted"
            ),
            ephemeral=True
        )
        
        # ========== MANDATORY DM TO USER ==========
        dm_embed = EmbedBuilder.dm_server_deleted(
            server_id=str(server_id),
            deleted_by=interaction.user.mention
        )
        
        await self.bot.send_user_dm(user, dm_embed)
        
        # Log action
        log_embed = EmbedBuilder.log_server_action(
            action="deleted",
            admin=interaction.user.mention,
            user=user.mention,
            server_info={'id': server_id, 'name': server_name}
        )
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="suspend", description="Suspend a server")
    @app_commands.describe(
        server_id="Server ID to suspend",
        user="User who owns the server",
        reason="Reason for suspension"
    )
    @is_admin()
    @not_in_maintenance()
    async def suspend_server(
        self,
        interaction: discord.Interaction,
        server_id: int,
        user: discord.User,
        reason: str = "Administrative action"
    ):
        """Suspend a server"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.suspend_server(server_id)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Suspension Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        # Success to admin
        await interaction.followup.send(
            embed=EmbedBuilder.success(
                "Server Suspended",
                f"Server ID {server_id} has been suspended"
            ),
            ephemeral=True
        )
        
        # ========== MANDATORY DM TO USER ==========
        dm_embed = EmbedBuilder.dm_server_suspended(
            server_id=str(server_id),
            reason=reason
        )
        
        await self.bot.send_user_dm(user, dm_embed)
        
        # Log action
        log_embed = EmbedBuilder.log_server_action(
            action="suspended",
            admin=interaction.user.mention,
            user=user.mention,
            server_info={'id': server_id}
        )
        log_embed.add_field(name="Reason", value=reason, inline=False)
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="unsuspend", description="Unsuspend a server")
    @app_commands.describe(
        server_id="Server ID to unsuspend",
        user="User who owns the server"
    )
    @is_admin()
    @not_in_maintenance()
    async def unsuspend_server(
        self,
        interaction: discord.Interaction,
        server_id: int,
        user: discord.User
    ):
        """Unsuspend a server"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.unsuspend_server(server_id)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Unsuspension Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        # Success to admin
        await interaction.followup.send(
            embed=EmbedBuilder.success(
                "Server Unsuspended",
                f"Server ID {server_id} has been restored"
            ),
            ephemeral=True
        )
        
        # ========== MANDATORY DM TO USER ==========
        dm_embed = EmbedBuilder.dm_server_unsuspended(server_id=str(server_id))
        
        await self.bot.send_user_dm(user, dm_embed)
        
        # Log action
        log_embed = EmbedBuilder.log_server_action(
            action="unsuspended",
            admin=interaction.user.mention,
            user=user.mention,
            server_info={'id': server_id}
        )
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="set_resources", description="Update server resources")
    @app_commands.describe(
        server_id="Server ID",
        user="User who owns the server",
        ram="New RAM in MB (optional)",
        cpu="New CPU percentage (optional)",
        disk="New disk space in MB (optional)"
    )
    @is_admin()
    @not_in_maintenance()
    async def set_resources(
        self,
        interaction: discord.Interaction,
        server_id: int,
        user: discord.User,
        ram: Optional[int] = None,
        cpu: Optional[int] = None,
        disk: Optional[int] = None
    ):
        """Update server resource limits"""
        await interaction.response.defer(ephemeral=True)
        
        if not any([ram, cpu, disk]):
            await interaction.followup.send(
                embed=EmbedBuilder.error("No Changes", "You must specify at least one resource to update"),
                ephemeral=True
            )
            return
        
        result = await self.api.update_server_build(server_id, ram=ram, cpu=cpu, disk=disk)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Update Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        # Success to admin
        changes = []
        if ram: changes.append(f"RAM: {ram} MB")
        if cpu: changes.append(f"CPU: {cpu}%")
        if disk: changes.append(f"Disk: {disk} MB")
        
        await interaction.followup.send(
            embed=EmbedBuilder.success(
                "Resources Updated",
                f"Server ID {server_id} resources updated:\n" + "\n".join(changes)
            ),
            ephemeral=True
        )
        
        # ========== MANDATORY DM TO USER ==========
        dm_embed = EmbedBuilder.dm_resources_updated(
            server_id=str(server_id),
            ram=ram,
            cpu=cpu,
            disk=disk
        )
        
        await self.bot.send_user_dm(user, dm_embed)
        
        # Log action
        log_embed = EmbedBuilder.log_server_action(
            action="updated",
            admin=interaction.user.mention,
            user=user.mention,
            server_info={
                'id': server_id,
                'resources': {'ram': ram, 'cpu': cpu, 'disk': disk}
            }
        )
        await self.bot.log_action(log_embed)
    
    @app_commands.command(name="list_servers", description="List all servers")
    @is_admin()
    async def list_servers(self, interaction: discord.Interaction, page: int = 1):
        """List servers with pagination"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_servers(page=page)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Failed to fetch servers", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        servers = result['data']['data']
        
        if not servers:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Servers", "No servers found on this page"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🖥️ Servers (Page {page})",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        for server in servers[:10]:
            attrs = server['attributes']
            status = "🔴 Suspended" if attrs.get('suspended') else "🟢 Active"
            embed.add_field(
                name=f"{attrs['name']} (ID: {attrs['id']})",
                value=f"Status: {status}\nUUID: `{attrs['uuid'][:16]}...`",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="server_info", description="Get detailed server information")
    @app_commands.describe(server_id="Server ID")
    @is_admin()
    async def server_info(self, interaction: discord.Interaction, server_id: int):
        """Display detailed server information"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.get_server(server_id)
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Server Not Found", f"Server ID {server_id} does not exist"),
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            embed=EmbedBuilder.server_info(result['data']),
            ephemeral=True
        )
    
    @app_commands.command(name="server_search", description="Search for servers by name")
    @app_commands.describe(name="Server name to search for")
    @is_admin()
    async def server_search(self, interaction: discord.Interaction, name: str):
        """Search servers by name"""
        await interaction.response.defer(ephemeral=True)
        
        result = await self.api.list_servers()
        
        if not result['success']:
            await interaction.followup.send(
                embed=EmbedBuilder.error("Search Failed", result.get('error', 'Unknown error')),
                ephemeral=True
            )
            return
        
        servers = result['data']['data']
        matches = [s for s in servers if name.lower() in s['attributes']['name'].lower()]
        
        if not matches:
            await interaction.followup.send(
                embed=EmbedBuilder.info("No Results", f"No servers found matching '{name}'"),
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results for '{name}'",
            color=discord.Color.blue()
        )
        
        for server in matches[:10]:
            attrs = server['attributes']
            embed.add_field(
                name=f"{attrs['name']} (ID: {attrs['id']})",
                value=f"UUID: `{attrs['uuid'][:16]}...`",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerCommands(bot))
