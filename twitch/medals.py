# twitch/medals.py

# =========================
# 🥇 MEDAL STATE (PER STREAM)
# =========================

_stream_active = False  # 🔴 medals only work when stream is live

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
# 🔄 STREAM LIFECYCLE
# =========================

def reset_medals():
    """Clear medal winners only"""
    for key in medals:
        medals[key] = None
    print("🥇 Medals reset")


def enable_medals():
    global _stream_active
    _stream_active = True
    print("🟢 Medals ENABLED (stream live)")


def end_stream():
    global _stream_active
    _stream_active = False
    reset_medals()
    print("🔴 Stream ended — medals disabled")




# =========================
# 🏅 HANDLE MEDAL MESSAGE
# =========================

async def handle_medal(message, content: str) -> bool:
    # Normalize input early
    word = content.lower().strip()
    if word.startswith("!"):
        word = word[1:]

    # 🚫 Stream offline
    if not _stream_active:
        if word in medals:
            await message.channel.send(
                "🔴 Stream is offline. Medals are disabled."
            )
            return True
        return False

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

    # User already claimed another medal
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
