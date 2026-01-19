import discord
from datetime import datetime
from typing import Optional

class EmbedBuilder:
    """Centralized embed builder for consistent styling"""
    
    @staticmethod
    def success(title: str, description: str = None, **kwargs) -> discord.Embed:
        """Green success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        for key, value in kwargs.items():
            embed.add_field(name=key, value=value, inline=True)
        return embed
    
    @staticmethod
    def error(title: str, description: str = None) -> discord.Embed:
        """Red error embed"""
        return discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def warning(title: str, description: str = None) -> discord.Embed:
        """Yellow warning embed"""
        return discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.yellow(),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def info(title: str, description: str = None) -> discord.Embed:
        """Blue info embed"""
        return discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
    
    # ==================== USER DM EMBEDS ====================
    
    @staticmethod
    def dm_server_created(server_name: str, server_id: str, node: str, ram: int, 
                         cpu: int, disk: int, version: str, panel_url: str, 
                         username: str, password: Optional[str] = None) -> discord.Embed:
        """DM embed when server is created"""
        embed = discord.Embed(
            title="✅ SERVER CREATED",
            description="Your new server has been successfully created!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="📛 Server Name", value=server_name, inline=True)
        embed.add_field(name="🆔 Server ID", value=server_id, inline=True)
        embed.add_field(name="🖥️ Node", value=node, inline=True)
        embed.add_field(name="💾 RAM", value=f"{ram} MB", inline=True)
        embed.add_field(name="⚙️ CPU", value=f"{cpu}%", inline=True)
        embed.add_field(name="💿 Disk", value=f"{disk} MB", inline=True)
        embed.add_field(name="🎮 Version", value=version, inline=True)
        embed.add_field(name="🌐 Panel URL", value=panel_url, inline=False)
        embed.add_field(name="👤 Username", value=username, inline=True)
        
        if password:
            embed.add_field(name="🔑 Password", value=f"||{password}||", inline=True)
            embed.add_field(name="⚠️ Important", value="Save your password! This is the only time you'll see it.", inline=False)
        
        embed.set_footer(text="Access your server at the panel URL above")
        return embed
    
    @staticmethod
    def dm_server_deleted(server_id: str, deleted_by: str) -> discord.Embed:
        """DM embed when server is deleted"""
        embed = discord.Embed(
            title="❌ SERVER DELETED",
            description="Your server has been permanently deleted.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Server ID", value=server_id, inline=True)
        embed.add_field(name="👮 Deleted By", value=deleted_by, inline=True)
        embed.add_field(name="📅 Date & Time", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        
        embed.set_footer(text="This action cannot be undone")
        return embed
    
    @staticmethod
    def dm_server_suspended(server_id: str, reason: str = "Administrative action") -> discord.Embed:
        """DM embed when server is suspended"""
        embed = discord.Embed(
            title="⚠️ SERVER SUSPENDED",
            description="Your server has been suspended and is temporarily unavailable.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Server ID", value=server_id, inline=True)
        embed.add_field(name="📋 Reason", value=reason, inline=False)
        embed.add_field(name="📅 Suspended At", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        
        embed.set_footer(text="Contact support if you believe this is an error")
        return embed
    
    @staticmethod
    def dm_server_unsuspended(server_id: str) -> discord.Embed:
        """DM embed when server is unsuspended"""
        embed = discord.Embed(
            title="✅ SERVER UNSUSPENDED",
            description="Your server has been restored and is now available again!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Server ID", value=server_id, inline=True)
        embed.add_field(name="📅 Restored At", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        
        embed.set_footer(text="Your server is now fully operational")
        return embed
    
    @staticmethod
    def dm_resources_updated(server_id: str, ram: int = None, cpu: int = None, 
                            disk: int = None) -> discord.Embed:
        """DM embed when server resources are updated"""
        embed = discord.Embed(
            title="🔧 SERVER RESOURCES UPDATED",
            description="Your server resources have been modified.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 Server ID", value=server_id, inline=False)
        
        changes = []
        if ram is not None:
            changes.append(f"💾 **RAM:** {ram} MB")
        if cpu is not None:
            changes.append(f"⚙️ **CPU:** {cpu}%")
        if disk is not None:
            changes.append(f"💿 **Disk:** {disk} MB")
        
        embed.add_field(name="📊 New Resources", value="\n".join(changes), inline=False)
        embed.add_field(name="📅 Updated At", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        
        embed.set_footer(text="Restart your server for changes to take full effect")
        return embed
    
    @staticmethod
    def dm_maintenance(enabled: bool, message: str = None) -> discord.Embed:
        """DM embed for maintenance mode notifications"""
        if enabled:
            embed = discord.Embed(
                title="🔧 MAINTENANCE MODE ENABLED",
                description=message or "The panel is currently undergoing maintenance. Your servers may be temporarily unavailable.",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="We'll notify you when maintenance is complete")
        else:
            embed = discord.Embed(
                title="✅ MAINTENANCE COMPLETE",
                description=message or "Maintenance has been completed. All services are now operational.",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Thank you for your patience")
        
        return embed
    
    # ==================== ADMIN LOG EMBEDS ====================
    
    @staticmethod
    def log_server_action(action: str, admin: str, user: str, server_info: dict) -> discord.Embed:
        """Log embed for server actions"""
        colors = {
            'created': discord.Color.green(),
            'deleted': discord.Color.red(),
            'suspended': discord.Color.orange(),
            'unsuspended': discord.Color.blue(),
            'updated': discord.Color.purple()
        }
        
        embed = discord.Embed(
            title=f"📋 Server {action.upper()}",
            color=colors.get(action.lower(), discord.Color.greyple()),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="👮 Admin", value=admin, inline=True)
        embed.add_field(name="👤 User", value=user, inline=True)
        embed.add_field(name="🆔 Server ID", value=server_info.get('id', 'N/A'), inline=True)
        
        if 'name' in server_info:
            embed.add_field(name="📛 Server Name", value=server_info['name'], inline=True)
        
        if 'resources' in server_info:
            res = server_info['resources']
            embed.add_field(
                name="📊 Resources",
                value=f"RAM: {res.get('ram', 'N/A')} MB\nCPU: {res.get('cpu', 'N/A')}%\nDisk: {res.get('disk', 'N/A')} MB",
                inline=True
            )
        
        return embed
    
    # ==================== INFO EMBEDS ====================
    
    @staticmethod
    def server_info(server_data: dict) -> discord.Embed:
        """Display server information"""
        attrs = server_data.get('attributes', {})
        limits = attrs.get('limits', {})
        
        embed = discord.Embed(
            title=f"🖥️ {attrs.get('name', 'Unknown Server')}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 ID", value=attrs.get('id', 'N/A'), inline=True)
        embed.add_field(name="🔑 UUID", value=attrs.get('uuid', 'N/A')[:8] + "...", inline=True)
        embed.add_field(name="📊 Status", value="🟢 Active" if not attrs.get('suspended') else "🔴 Suspended", inline=True)
        
        embed.add_field(name="💾 RAM", value=f"{limits.get('memory', 0)} MB", inline=True)
        embed.add_field(name="⚙️ CPU", value=f"{limits.get('cpu', 0)}%", inline=True)
        embed.add_field(name="💿 Disk", value=f"{limits.get('disk', 0)} MB", inline=True)
        
        embed.set_footer(text=f"Server UUID: {attrs.get('uuid', 'N/A')}")
        return embed
    
    @staticmethod
    def node_info(node_data: dict) -> discord.Embed:
        """Display node information"""
        attrs = node_data.get('attributes', {})
        
        embed = discord.Embed(
            title=f"🖥️ {attrs.get('name', 'Unknown Node')}",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="🆔 ID", value=attrs.get('id', 'N/A'), inline=True)
        embed.add_field(name="🌐 FQDN", value=attrs.get('fqdn', 'N/A'), inline=True)
        embed.add_field(name="📍 Location", value=attrs.get('location_id', 'N/A'), inline=True)
        
        embed.add_field(name="💾 Memory", value=f"{attrs.get('memory', 0)} MB", inline=True)
        embed.add_field(name="💿 Disk", value=f"{attrs.get('disk', 0)} MB", inline=True)
        embed.add_field(name="🔌 Daemon Port", value=attrs.get('daemon_listen', 'N/A'), inline=True)
        
        return embed
