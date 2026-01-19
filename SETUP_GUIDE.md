# Pterodactyl Discord Bot - Complete Setup Guide

## 📋 Prerequisites

- Python 3.10 or higher
- A Discord Bot Token
- Pterodactyl Panel with API access
- Application API Key (for admin actions)
- Client API Key (for server operations)

---

## 🚀 Quick Start

### 1. Clone or Download the Bot

Create the following directory structure:

```
pterodactyl-bot/
├── bot.py
├── .env
├── requirements.txt
├── cogs/
│   ├── __init__.py
│   ├── servers.py
│   ├── users.py
│   ├── panel.py
│   └── utility.py
└── utils/
    ├── __init__.py
    ├── api.py
    ├── embeds.py
    └── checks.py
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section
4. Click "Add Bot"
5. Enable these **Privileged Gateway Intents**:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Copy your bot token
7. Go to OAuth2 → URL Generator
8. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
9. Select permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
10. Copy the generated URL and invite the bot to your server

### 4. Get Pterodactyl API Keys

#### Application API Key (Admin Actions)
1. Login to your Pterodactyl Panel
2. Go to **Account Settings** → **API Credentials**
3. Click "Create New" for **Application API**
4. Give it a description: "Discord Bot"
5. Select permissions:
   - ✅ All permissions (or minimum: users, servers, nodes, nests)
6. Copy the key (starts with `ptla_`)

#### Client API Key (Server Operations)
1. Still in API Credentials
2. Click "Create New" for **Account API**
3. Description: "Discord Bot Client"
4. Copy the key (starts with `ptlc_`)

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
PANEL_URL=https://panel.example.com
APP_API_KEY=ptla_your_application_api_key_here
CLIENT_API_KEY=ptlc_your_client_api_key_here
ADMIN_IDS=123456789012345678,987654321098765432
LOG_CHANNEL_ID=123456789012345678
```

**How to get Discord IDs:**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your username → Copy ID
3. Right-click on a channel → Copy ID

### 6. Create Empty `__init__.py` Files

```bash
touch cogs/__init__.py
touch utils/__init__.py
```

### 7. Run the Bot

```bash
python bot.py
```

You should see:
```
✅ Loaded cogs.servers
✅ Loaded cogs.users
✅ Loaded cogs.panel
✅ Loaded cogs.utility
✅ Commands synced
✅ BotName#1234 is online!
📊 Servers: 1
👥 Admin IDs: [123456789012345678]
```

---

## 🔐 Security Best Practices

### Environment Variables
- **Never commit `.env` to Git**
- Add `.env` to your `.gitignore`
- Use strong, unique API keys
- Rotate API keys regularly

### Admin Access
- Only add trusted users to `ADMIN_IDS`
- Regularly audit admin list
- Use ephemeral responses for sensitive data

### API Keys
- Store Application and Client API keys separately
- Use minimum required permissions
- Revoke unused keys immediately

---

## 📝 Command Reference

### Server Management (Admin Only)

#### `/createserver`
Creates a new server for a user.
- **Required:** name, ram, cpu, disk, version, node_id, egg_id, user
- **Effect:** Sends DM to user with server details and credentials

#### `/delete_server`
Permanently deletes a server.
- **Required:** server_id, user
- **Effect:** Sends deletion notification DM to user
- **Warning:** Irreversible action

#### `/suspend`
Suspends a server, making it unavailable.
- **Required:** server_id, user
- **Optional:** reason
- **Effect:** Sends suspension notification DM to user

#### `/unsuspend`
Restores a suspended server.
- **Required:** server_id, user
- **Effect:** Sends restoration notification DM to user

#### `/set_resources`
Updates server RAM, CPU, or Disk.
- **Required:** server_id, user
- **Optional:** ram, cpu, disk (at least one required)
- **Effect:** Sends resource update notification DM to user

#### `/list_servers`
Lists all servers with pagination.

#### `/server_info`
Shows detailed information about a specific server.

#### `/server_search`
Searches for servers by name.

### User Management (Admin Only)

#### `/user_list`
Lists all Pterodactyl panel users.

#### `/user_search`
Searches for a user by email or username.

#### `/delete_user`
Deletes a user and all their servers.
- **Warning:** Requires confirmation

#### `/change_password`
Changes a user's password or generates a random one.

### Panel & Infrastructure (Admin Only)

#### `/nodes`
Lists all panel nodes with status.

#### `/eggs`
Lists available eggs for server creation.

#### `/panel_status`
Checks if the panel API is reachable.

#### `/backup_list`
Lists backups for a specific server.

#### `/maintenance_on`
Enables maintenance mode (blocks non-admin commands).

#### `/maintenance_off`
Disables maintenance mode.

### Utility Commands

#### `/ping`
Shows bot latency.

#### `/help`
Displays all available commands.

#### `/manage`
Shows interactive management panel (Admin only).

#### `/stats`
Displays bot statistics and uptime.

---

## 🔔 DM Notification System

**Critical Feature:** All server actions automatically send DMs to affected users.

### When Users Receive DMs:

1. **Server Created**
   - Server details (name, ID, resources)
   - Panel URL
   - Username
   - Password (if new user)

2. **Server Deleted**
   - Server ID
   - Who deleted it
   - Timestamp

3. **Server Suspended**
   - Server ID
   - Reason
   - Timestamp

4. **Server Unsuspended**
   - Server ID
   - Restored timestamp

5. **Resources Updated**
   - Server ID
   - New RAM/CPU/Disk values
   - Update timestamp

### DM Failure Handling

If a user has DMs disabled:
- Bot logs failure in admin log channel
- Includes user mention and reason
- Admin is still notified of action success

---

## 📊 Logging System

All admin actions are logged to `LOG_CHANNEL_ID`:

- Server creations, deletions, suspensions
- Resource modifications
- User deletions
- Password changes
- Maintenance mode toggles
- DM delivery failures

**Log Format:**
- Timestamp
- Admin who performed action
- Affected user
- Action details
- DM delivery status

---

## ⚙️ Resource Limits

### Default Validation Ranges:

- **RAM:** 512 MB - 32768 MB (32 GB)
- **CPU:** 50% - 400%
- **Disk:** 1024 MB (1 GB) - 102400 MB (100 GB)

To modify these limits, edit the validation in `cogs/servers.py`:

```python
if ram < 512 or ram > 32768:  # Adjust these values
```

---

## 🐛 Troubleshooting

### Bot Won't Start

**Error:** `Missing required environment variables`
- **Solution:** Verify all variables in `.env` are set correctly

**Error:** `Failed to load cogs`
- **Solution:** Ensure `__init__.py` exists in `cogs/` and `utils/`

### Commands Not Showing

**Problem:** Slash commands don't appear in Discord
- **Solution:** 
  1. Ensure bot has `applications.commands` scope
  2. Wait 1-2 minutes for Discord to sync
  3. Kick and re-invite the bot with correct permissions

### API Connection Failed

**Error:** `Failed to connect to panel`
- **Solution:**
  1. Verify `PANEL_URL` is correct (no trailing slash)
  2. Check API keys are valid
  3. Ensure panel is accessible from bot's network
  4. Test with `/panel_status`

### DMs Not Sending

**Problem:** Users not receiving DMs
- **Solution:**
  1. User may have DMs disabled (check log channel for failures)
  2. Bot and user must share a server
  3. User hasn't blocked the bot

### Permission Denied

**Error:** Admin commands not working
- **Solution:**
  1. Verify your Discord ID is in `ADMIN_IDS`
  2. Use Developer Mode to copy your ID correctly
  3. Restart bot after changing `.env`

---

## 🔄 Updating the Bot

1. **Backup your `.env` file**
2. Download new code
3. Install updated dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. Restart the bot

---

## 📂 Project Structure Explained

```
pterodactyl-bot/
├── bot.py                 # Main bot file, loads cogs
├── .env                   # Configuration (DO NOT COMMIT)
├── requirements.txt       # Python dependencies
│
├── cogs/                  # Command modules
│   ├── servers.py        # Server management commands
│   ├── users.py          # User management commands
│   ├── panel.py          # Panel/infrastructure commands
│   └── utility.py        # Utility commands (ping, help, etc)
│
└── utils/                 # Utility modules
    ├── api.py            # Pterodactyl API wrapper
    ├── embeds.py         # Embed templates
    └── checks.py         # Permission checks
```

---

## 🎯 Node & Egg IDs

### Finding Node IDs
1. Run `/nodes` in Discord
2. Note the ID in parentheses
3. Use this ID when creating servers

### Finding Egg IDs
1. Run `/eggs` in Discord (default shows Minecraft eggs)
2. For other games: `/eggs nest_id:2` (e.g., 2 for Source games)
3. Common nests:
   - 1: Minecraft
   - 2: Source Engine
   - 3: Voice Servers
   - 5: Rust

---

## 📈 Production Deployment

### Using systemd (Linux)

1. Create service file:
```bash
sudo nano /etc/systemd/system/pterodactyl-bot.service
```

2. Add configuration:
```ini
[Unit]
Description=Pterodactyl Discord Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/pterodactyl-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable pterodactyl-bot
sudo systemctl start pterodactyl-bot
sudo systemctl status pterodactyl-bot
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t pterodactyl-bot .
docker run -d --name ptero-bot --env-file .env pterodactyl-bot
```

---

## 🆘 Support

### Common Issues

1. **"Invalid Node/Egg ID"** - Run `/nodes` or `/eggs` to get valid IDs
2. **"User has DMs disabled"** - Check log channel for notification
3. **"API rate limit"** - Wait a minute and try again
4. **"Server creation failed"** - Ensure node has available allocations

### Getting Help

- Check this guide thoroughly
- Review error messages in console
- Verify all API keys and IDs
- Test panel API with `/panel_status`

---

## ✅ Post-Setup Checklist

- [ ] Bot is online and showing in Discord
- [ ] `/ping` responds successfully
- [ ] `/panel_status` shows green
- [ ] `/nodes` lists your nodes
- [ ] `/eggs` lists available eggs
- [ ] Created a test server with `/createserver`
- [ ] Received DM notification as test user
- [ ] Log channel receives action logs
- [ ] Admin commands are restricted properly
- [ ] Non-admin users cannot use restricted commands

---

## 🎉 You're Ready!

Your Pterodactyl Discord Bot is now fully operational and ready to manage your game servers with automatic user notifications!

**Remember:** All server actions automatically notify users via DM. If DMs fail, check your log channel for details.
