# twitch/medals.py

# =========================
# 🥇 MEDAL STATE (PER STREAM)
# =========================

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
# RESET (call on stream start)
# =========================

def reset_medals():
    for key in medals:
        medals[key] = None


# =========================
# HANDLE MEDAL MESSAGE
# =========================

async def handle_medal(message, content: str) -> bool:
    # normalize input:
    # - lowercase
    # - remove leading "!"
    word = content.lower().strip()
    if word.startswith("!"):
        word = word[1:]

    # Not a medal keyword
    if word not in medals:
        return False

    user = message.author.name
    current_winner = medals[word]

    # Medal already claimed
    if current_winner is not None:
        await message.channel.send(
            f"{MEDAL_EMOTES[word]} {word.upper()} is already claimed by @{current_winner}!"
        )
        return True

    # User already won another medal
    if user in medals.values():
        await message.channel.send(
            f"@{user} you already claimed a medal 😅"
        )
        return True

    # Assign medal
    medals[word] = user

    await message.channel.send(
        f"{MEDAL_EMOTES[word]} @{user} {MEDAL_TEXT[word]}"
    )

    return True
