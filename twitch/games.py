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
SPANK_EMOTES = [
    "itsfro31Spank1", 
]

KILL_COOLDOWN = 20  # seconds
kill_cooldowns = {}


# =========================
# ⚔️ HANDLE !kill
# =========================

async def handle_kill(message, content: str) -> bool:
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

    # 🛡️ PROTECTED TARGETS (bot + broadcaster)
    bot_name = message.channel._client.nick.lower()
    broadcaster_name = message.channel.name.lower()

    if target.lower() in {bot_name, broadcaster_name}:
        # backfire
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
# 🍑 HANDLE !spank
# =========================

async def handle_spank(message, content: str) -> bool:
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

    # 🛡️ PROTECTED TARGETS
    bot_name = message._client.user.name.lower()

    if target.lower() == bot_name:
        await message.channel.send(
            f"⛔ @{attacker} tried to spank me? Naughty 😏"
        )
        return True

    if message.author.is_broadcaster and target.lower() == attacker.lower():
        await message.channel.send(
            f"😳 Even I won’t allow that!"
        )
        return True

    if target.lower() == message.channel.name.lower():
        await message.channel.send(
            f"⛔ You can’t spank the broadcaster 😈"
        )
        return True

    emote = random.choice(SPANK_EMOTES)

    await message.channel.send(
        f"{emote} 😈 @{attacker} spanked @{target}!"
    )

    return True


