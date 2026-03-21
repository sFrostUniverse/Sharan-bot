import sqlite3
import time
from pathlib import Path

DB_PATH = Path("data/bot.db")


class TwitchDatabase:
    def __init__(self):
        DB_PATH.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    # =========================
    # 🧱 TABLES
    # =========================
    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS twitch_users (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    gold INTEGER DEFAULT 0,
                    silver INTEGER DEFAULT 0,
                    bronze INTEGER DEFAULT 0,
                    last_daily INTEGER DEFAULT 0,
                    first_seen INTEGER DEFAULT 0,
                    last_seen INTEGER DEFAULT 0
                )
            """)

    # =========================
    # 👤 USER TRACKING
    # =========================
    def ensure_user(self, username: str):
        now = int(time.time())
        with self.conn:
            self.conn.execute("""
                INSERT OR IGNORE INTO twitch_users
                (username, first_seen, last_seen)
                VALUES (?, ?, ?)
            """, (username, now, now))

    def update_last_seen(self, username: str):
        with self.conn:
            self.conn.execute("""
                UPDATE twitch_users
                SET last_seen = ?
                WHERE username = ?
            """, (int(time.time()), username))

    # =========================
    # 💰 POINTS
    # =========================
    def get_points(self, username: str) -> int:
        self.ensure_user(username)
        cur = self.conn.execute(
            "SELECT points FROM twitch_users WHERE username = ?",
            (username,)
        )
        return cur.fetchone()["points"]

    def add_points(self, username: str, amount: int):
        self.ensure_user(username)
        with self.conn:
            self.conn.execute("""
                UPDATE twitch_users
                SET points = points + ?
                WHERE username = ?
            """, (amount, username))

    # =========================
    # 🎁 DAILY
    # =========================
    def can_claim_daily(self, username: str) -> bool:
        self.ensure_user(username)
        cur = self.conn.execute(
            "SELECT last_daily FROM twitch_users WHERE username = ?",
            (username,)
        )
        last = cur.fetchone()["last_daily"]
        return time.time() - last >= 86400

    def claim_daily(self, username: str, reward: int):
        if not self.can_claim_daily(username):
            return False

        with self.conn:
            self.conn.execute("""
                UPDATE twitch_users
                SET points = points + ?, last_daily = ?
                WHERE username = ?
            """, (reward, int(time.time()), username))

        return True

    # =========================
    # 🏅 MEDALS
    # =========================
    def add_medal(self, username: str, medal: str):
        if medal not in ("gold", "silver", "bronze"):
            return

        self.ensure_user(username)
        with self.conn:
            self.conn.execute(f"""
                UPDATE twitch_users
                SET {medal} = {medal} + 1
                WHERE username = ?
            """, (username,))

    def get_medals(self, username: str) -> dict:
        self.ensure_user(username)
        cur = self.conn.execute("""
            SELECT gold, silver, bronze
            FROM twitch_users
            WHERE username = ?
        """, (username,))
        row = cur.fetchone()
        return {
            "gold": row["gold"],
            "silver": row["silver"],
            "bronze": row["bronze"],
        }