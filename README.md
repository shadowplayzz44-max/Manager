# 🦖 Pterodactyl Discord Bot

A comprehensive, production-ready Discord bot for managing Pterodactyl game server panels with **mandatory user DM notifications** for all server actions.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3.0+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

### 🔔 Mandatory DM Notification System
- **Every server action** automatically sends a DM to the affected user
- DM delivery failure logging in admin channel
- Professional, formatted notifications with all relevant details
- New user credentials sent securely via DM

### 🖥️ Complete Server Management
- Create servers with custom resources
- Delete, suspend, and unsuspend servers
- Update server resources (RAM, CPU, Disk)
- List, search, and view detailed server information
- Full confirmation system for destructive actions

### 👥 User Management
- List and search Pterodactyl users
- Delete users (with all their servers)
- Change user passwords
- Automatic user creation when needed

### 🛠️ Panel Infrastructure
- View all nodes and their status
- List available eggs for server creation
- Check panel API connectivity
- Backup management
- Maintenance mode

### 🔐 Advanced Security
- Admin-only command restrictions
- Ephemeral responses for sensitive data
- Environment variable protection
- Permission validation system
- Confirmation views for destructive actions

### 📊 Comprehensive Logging
- All admin actions logged to dedicated channel
- DM delivery status tracking
- Timestamp and user attribution
- Color-coded embeds for quick identification

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Pterodactyl Panel with API access
- Application API Key
- Client API Key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd pterodactyl-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

4. **Create required directories**
```bash
mkdir -p cogs utils
touch cogs/__init__.py utils/__init__.py
```

5. **Run the bot**
```bash
python bot.py
```

## 📋 Configuration

Edit `.env` with your credentials:

```env
DISCORD_TOKEN=your_discord_bot_token
PANEL_URL=https://panel.example.com
APP_API_KEY=ptla_your_application_key
CLIENT_API_KEY=ptlc_your_client_key
ADMIN_IDS=123456789012345678,987654321098765432
LOG_CHANNEL_ID=123456789012345678
```

## 📚 Commands Overview

### Server Management (Admin Only)
- `/createserver` - Create a new server (sends DM)
- `/delete_server` - Delete a server (sends DM)
- `/suspend` - Suspend a server (sends DM)
- `/unsuspend` - Restore a server (sends DM)
- `/set_resources` - Update resources (sends DM)
- `/list_servers` - List all servers
- `/server_info` - Get server details
- `/server_search` - Search servers by name

### User Management (Admin Only)
- `/user_list` - List all panel users
- `/user_search` - Search for users
- `/delete_user` - Remove a user
- `/change_password` - Update user password

### Panel & Infrastructure (Admin Only)
- `/nodes` - View all nodes
- `/eggs` - List available eggs
- `/panel_status` - Check API status
- `/backup_list` - View server backups
- `/maintenance_on` - Enable maintenance mode
- `/maintenance_off` - Disable maintenance mode

### Utility Commands
- `/ping` - Check bot latency
- `/help` - Show all commands
- `/manage` - Interactive management panel
- `/stats` - Bot statistics

## 🔔 DM Notification Details

### Users receive DMs for:
1. **Server Creation** - Full details including credentials for new users
2. **Server Deletion** - Confirmation with admin and timestamp
3. **Server Suspension** - Reason and timestamp
4. **Server Restoration** - Confirmation message
5. **Resource Updates** - New RAM/CPU/Disk values

### DM Failure Handling
- If user has DMs disabled, admin is notified in log channel
- Action still completes successfully
- Admin can manually inform user

## 🏗️ Project Structure

```
pterodactyl-bot/
├── bot.py                 # Main bot initialization
├── .env                   # Configuration (not in git)
├── requirements.txt       # Python dependencies
├── cogs/
│   ├── servers.py        # Server management commands
│   ├── users.py          # User management commands
│   ├── panel.py          # Panel infrastructure commands
│   └── utility.py        # Utility commands
└── utils/
    ├── api.py            # Pterodactyl API wrapper
    ├── embeds.py         # Embed templates
    └── checks.py         # Permission checks
```

## 🔐 Security Features

- ✅ Admin-only command restrictions
- ✅ Ephemeral responses for sensitive data
- ✅ Environment variable encryption
- ✅ API key separation (Application vs Client)
- ✅ Confirmation prompts for destructive actions
- ✅ DM delivery validation
- ✅ Comprehensive action logging

## 📖 Documentation

For detailed setup instructions, troubleshooting, and advanced configuration, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## 🐛 Common Issues

### Bot commands not appearing?
- Ensure bot has `applications.commands` scope
- Wait 1-2 minutes for Discord to sync
- Re-invite bot with correct permissions

### DMs not sending?
- Check if user has DMs disabled (logged in admin channel)
- Verify bot and user share a server
- Ensure user hasn't blocked the bot

### API connection failed?
- Verify `PANEL_URL` is correct (no trailing slash)
- Test API keys in panel
- Run `/panel_status` to diagnose

## 🎯 Resource Limits

Default validation ranges:
- **RAM:** 512 MB - 32 GB
- **CPU:** 50% - 400%
- **Disk:** 1 GB - 100 GB

Modify in `cogs/servers.py` as needed.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This bot is not officially affiliated with Pterodactyl Panel. Use at your own risk. Always backup your panel data before using automated management tools.

## 🙏 Acknowledgments

- [Pterodactyl Panel](https://pterodactyl.io/) - The game server management panel
- [discord.py](https://github.com/Rapptz/discord.py) - Python Discord API wrapper
- All contributors and users of this bot

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed documentation
- Review common issues section above

---

**Made with ❤️ for the Pterodactyl community**
