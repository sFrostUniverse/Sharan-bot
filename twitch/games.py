# twitch/games.py

import time
import random

# =========================
# ⚔️ KILL GAME CONFIG
# =========================

KILL_WEAPONS = [
    "itsfro31Bang",
]

KILL_RESULTS = [
    "itsfro31Fear",
]

KILL_COOLDOWN = 20  # seconds
kill_cooldowns = {}

# =========================
# 🔨 BONK GAME CONFIG
# =========================

BONK_EMOTES = [
    "itsfro31Bullyyy",
]

# =========================
# ⚔️ HANDLE !kill
# =========================

async def handle_kill(message, content: str, bot_name: str) -> bool:
    content = content.strip()

    if not content.lower().startswith("!kill"):
        return False

    parts = content.split()
    if len(parts) < 2:
        await message.channel.send(
            f"@{message.author.name} usage: !kill @username"
        )
        return True

    attacker = message.author.name
    target = parts[1].lstrip("@")

    # ❌ no self kill
    if target.lower() == attacker.lower():
        await message.channel.send(
            f"@{attacker} you can’t kill yourself 😅"
        )
        return True

    broadcaster_name = message.channel.name.lower()

    # 🛡️ PROTECTED TARGETS (BOT OR BROADCASTER)
    if target.lower() in {bot_name.lower(), broadcaster_name}:
        weapon = random.choice(KILL_WEAPONS)
        result = random.choice(KILL_RESULTS)

        await message.channel.send(
            f"💥 Backfire! @{target} {weapon} {result} @{attacker} 😈"
        )
        return True

    # ⏱️ cooldown
    now = time.time()
    last = kill_cooldowns.get(attacker, 0)

    if now - last < KILL_COOLDOWN:
        await message.channel.send(
            f"@{attacker} cooldown! Try again in a moment ⏳"
        )
        return True

    kill_cooldowns[attacker] = now

    weapon = random.choice(KILL_WEAPONS)
    result = random.choice(KILL_RESULTS)

    await message.channel.send(
        f"@{attacker} {weapon} {result} @{target}"
    )
    return True


# =========================
# 🔨 HANDLE !bonk
# =========================

async def handle_bonk(message, content: str, bot_name: str) -> bool:
    content = content.strip()

    if not content.lower().startswith("!bonk"):
        return False

    parts = content.split()
    if len(parts) < 2:
        await message.channel.send(
            f"@{message.author.name} usage: !bonk @username"
        )
        return True

    attacker = message.author.name
    target = parts[1].lstrip("@")

    # ❌ no self bonk
    if target.lower() == attacker.lower():
        await message.channel.send(
            f"@{attacker} bonking yourself? BONKED 😳"
        )
        return True

    broadcaster_name = message.channel.name.lower()

    # 🛡️ PROTECTED TARGETS (BOT OR BROADCASTER)
    if target.lower() in {bot_name.lower(), broadcaster_name}:
        await message.channel.send(
            f"⛔ @{attacker} tried to bonk @{target} and got denied 😈"
        )
        return True

    emote = random.choice(BONK_EMOTES)

    await message.channel.send(
        f"{emote} 🔨 @{attacker} bonked @{target}!"
    )
    return True
