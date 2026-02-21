# Sharan Discord Bot

Sharan is a **multi-purpose Discord bot** focused on **Twitch stream notifications** and **automation utilities**.  
It is **not** a voice-channel creation bot (that is Rishika).

This README is specifically for **Sharan**.

---

## 🎯 Features

### 🎮 Twitch Live Notifications
- Notify Discord channels when a Twitch streamer goes **LIVE**
- Optional **role ping**
- One-time notification per stream (no spam)
- Automatic LIVE / OFFLINE detection

### 📢 Announcement Channel Status
- Automatically renames a configured channel:
  - `🔴 username-live`
  - `⚫ username-offline`

### 🧩 Slash Commands
- `/twitch add` – Add Twitch alerts (username, role, announcement channel)
- `/twitch list` – View configured Twitch alerts
- `/twitch remove` – Remove a Twitch streamer

### 🔒 Secure by Design
- Uses Twitch **App Access Tokens**
- No user OAuth tokens stored
- Secrets stored only in environment variables
- Database stored locally per deployment

---

## 🧠 What Sharan Is NOT
❌ Not a voice-channel creation bot  
❌ Not a moderation bot  
❌ Not a music bot  

👉 Voice channel features belong to **Rishika Bot**.

---

## ⚙️ Required Permissions

**Bot Permissions**
- View Channels
- Send Messages
- Embed Links
- Manage Channels (for announcement renaming)
- Mention Roles (optional)

**OAuth Scopes**
- `bot`
- `applications.commands`

---

## 🔧 Environment Variables

```env
DISCORD_TOKEN=your_discord_bot_token

TWITCH_CLIENT_ID=your_twitch_client_id
TWITCH_CLIENT_SECRET=your_twitch_client_secret
```

---

## 🗄 Database

Uses SQLite:
```
data/sharanbot.db
```

Stores:
- Guild ID
- Channel ID
- Role ID
- Twitch username & user ID
- Live status & last stream ID

---

## 🚀 Deployment

- Designed for **cloud hosting** (Render, VPS, Apollo, etc.)
- Supports **24/7 operation**
- Can run alongside FastAPI services

---

## 🔐 Security & Privacy

- No personal user data stored
- No message content logged
- Only configuration data is persisted
- Tokens never exposed publicly

See `PRIVACY.md` and `TERMS.md` for full policies.

---

## 🧑‍💻 Maintained By

**Froséa**
Discord automation & streaming tools

---

## 📜 License
MIT
