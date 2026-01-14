# twitch/medals.py

medals = {
    "first": None,
    "second": None,
    "third": None,
}

MEDAL_EMOTES = {
    "first": "🥇",
    "second": "🥈",
    "third": "🥉",
}

MEDAL_TEXT = {
    "first": "got FIRST place! GG 🎉",
    "second": "got SECOND place! Nice!",
    "third": "got THIRD place! Clap clap 👏",
}

# =========================
# 🧹 MANUAL RESET
# =========================

def reset_medals():
    for key in medals:
        medals[key] = None
    print("♻️ Medals reset manually")

# =========================
# 🏅 HANDLE MEDALS
# =========================

async def handle_medal(message, content: str) -> bool:
    word = content.lower().strip()
    if word.startswith("!"):
        word = word[1:]

    if word not in medals:
        return False

    user = message.author.name

    # Medal already claimed
    if medals[word] is not None:
        await message.channel.send(
            f"{MEDAL_EMOTES[word]} {word.upper()} already claimed by @{medals[word]}!"
        )
        return True

    # User already has a medal
    if user in medals.values():
        await message.channel.send(
            f"@{user} you already claimed a medal 😅"
        )
        return True

    medals[word] = user
    await message.channel.send(
        f"{MEDAL_EMOTES[word]} @{user} {MEDAL_TEXT[word]}"
    )
    return True
