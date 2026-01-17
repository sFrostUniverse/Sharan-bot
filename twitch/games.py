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
# 🍑 SPANK GAME CONFIG
# =========================

SPANK_EMOTES = [
    "itsfro31Spank1",
    "itsfro31Spank2",
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

    # 🛡️ protected targets (bot + broadcaster)
    if target.lower() == bot_name.lower() or message.author.is_broadcaster:
        weapon = random.choice(KILL_WEAPONS)
        result = random.choice(KILL_RESULTS)

        await message.channel.send(
            f"💥 Backfire! @{bot_name} {weapon} {result} @{attacker} 😈"
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
# 🍑 HANDLE !spank
# =========================

async def handle_spank(message, content: str, bot_name: str) -> bool:
    content = content.strip()

    if not content.lower().startswith("!spank"):
        return False

    parts = content.split()
    if len(parts) < 2:
        await message.channel.send(
            f"@{message.author.name} usage: !spank @username"
        )
        return True

    attacker = message.author.name
    target = parts[1].lstrip("@")

    # ❌ no self spank
    if target.lower() == attacker.lower():
        await message.channel.send(
            f"@{attacker} spanking yourself? That’s wild 😳"
        )
        return True

    # 🛡️ protected targets (bot + broadcaster)
    if target.lower() == bot_name.lower() or message.author.is_broadcaster:
        await message.channel.send(
            f"⛔ @{attacker} tried to spank @{target} and got denied 😈"
        )
        return True

    emote = random.choice(SPANK_EMOTES)

    await message.channel.send(
        f"{emote} 😈 @{attacker} spanked @{target}!"
    )
    return True
