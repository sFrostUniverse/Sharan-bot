import random
import time
from typing import Dict
from twitch.medals import get_user_medals

from twitch.points import (
    get_points,
    claim_daily,
    gamble_points,
)
# =========================
# 📜 COMMAND REGISTRY
# =========================
COMMAND_LIST = {
    "!help": {
        "desc": "Show available commands",
        "show": True,
    },
    "!hype": {
        "desc": "Hype the chat",
        "show": True,
    },
    "!lurk": {
        "desc": "Go lurk mode",
        "show": True,
    },
    "!coinflip": {
        "desc": "Flip a coin",
        "show": True,
    },
    "!roll": {
        "desc": "Roll a number (1–100)",
        "show": True,
    },
    "!love": {
        "desc": "Send love to someone",
        "show": True,
    },
    "!kill": {
        "desc": "Attempt to kill someone 😈",
        "show": True,
    },
    "!bonk": {
        "desc": "Bonk someone to horny jail 🔨",
        "show": True,
    },
    "!points": {
    "desc": "Check your points",
    "show": True,
    },
    "!daily": {
        "desc": "Claim daily points",
        "show": True,
    },
    "!gamble": {
        "desc": "Gamble your points",
        "show": True,
    },
}

# =========================
# ⏱️ COOLDOWNS
# =========================
USER_COOLDOWN = 15  # seconds
last_used: Dict[str, float] = {}

def on_cooldown(user: str) -> bool:
    now = time.time()
    last = last_used.get(user, 0)
    if now - last < USER_COOLDOWN:
        return True
    last_used[user] = now
    return False


# =========================
# 🎉 COMMAND HANDLERS
# =========================

async def handle_fun_commands(bot, message) -> bool:
    content = message.content.lower().strip()
    user = message.author.name

    # =========================
    # 📜 !help
    # =========================
    if content == "!help":
        visible_commands = [
            cmd for cmd, meta in COMMAND_LIST.items()
            if meta.get("show", False)
        ]

        commands_text = " | ".join(visible_commands)

        await message.channel.send(
            f"📜 Available commands: {commands_text}"
        )
        return True

    # Mods bypass cooldown
    if not (message.author.is_mod or message.author.is_broadcaster):
        if on_cooldown(user):
            return True

    # =========================
    # 🔥 !hype
    # =========================
    if content == "!hype":
        await message.channel.send(
            "🔥🔥 HYPE TRAIN! LET’S GOOO 🔥🔥"
        )
        return True

    # =========================
    # 👀 !lurk
    # =========================
    if content == "!lurk":
        await message.channel.send(
            f"👀 @{user} is now lurking… thanks for the support 💜"
        )
        return True

    # =========================
    # 🪙 !coinflip
    # =========================
    if content == "!coinflip":
        result = random.choice(["HEADS 🪙", "TAILS 🪙"])
        await message.channel.send(
            f"🪙 @{user} flipped… {result}"
        )
        return True

    # =========================
    # 🎲 !roll
    # =========================
    if content == "!roll":
        roll = random.randint(1, 100)
        await message.channel.send(
            f"🎲 @{user} rolled a {roll}"
        )
        return True

    # =========================
    # ❤️ !love @user
    # =========================
    if content.startswith("!love"):
        parts = content.split()
        if len(parts) >= 2:
            target = parts[1].lstrip("@")
            await message.channel.send(
                f"💜 @{user} sends love to @{target} 💜"
            )
        else:
            await message.channel.send(
                f"💜 @{user} sends love to everyone 💜"
            )
        return True

    return False