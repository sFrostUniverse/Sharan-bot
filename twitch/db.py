import sqlite3
import threading
import time
import os

# =========================
# 📁 DATABASE PATH
# =========================
DB_PATH = "data/bot.db"
os.makedirs("data", exist_ok=True)

# =========================
# 🔒 SQLITE WRITE LOCK
# =========================
_db_lock = threading.Lock()


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    # =========================
    # 🧱 TABLE SETUP
    # =========================
    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    gold INTEGER DEFAULT 0,
                    silver INTEGER DEFAULT 0,
                    bronze INTEGER DEFAULT 0,
                    last_daily INTEGER DEFAULT 0
                )
            """)

    # =========================
    # 👤 ENSURE USER EXISTS
    # =========================
    def ensure_user(self, username: str):
        with _db_lock:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO users (username) VALUES (?)",
                    (username,)
                )

    # =========================
    # 💰 POINTS
    # =========================
    def get_points(self, username: str) -> int:
        self.ensure_user(username)
        cur = self.conn.execute(
            "SELECT points FROM users WHERE username = ?",
            (username,)
        )
        return cur.fetchone()["points"]

    def add_points(self, username: str, amount: int):
        self.ensure_user(username)
        with _db_lock:
            with self.conn:
                self.conn.execute(
                    "UPDATE users SET points = points + ? WHERE username = ?",
                    (amount, username)
                )

    # =========================
    # 🎁 DAILY CLAIM
    # =========================
    def can_claim_daily(self, username: str) -> bool:
        self.ensure_user(username)
        cur = self.conn.execute(
            "SELECT last_daily FROM users WHERE username = ?",
            (username,)
        )
        last = cur.fetchone()["last_daily"]
        return time.time() - last >= 86400  # 24 hours

    def claim_daily(self, username: str) -> bool:
        if not self.can_claim_daily(username):
            return False

        with _db_lock:
            with self.conn:
                self.conn.execute(
                    """
                    UPDATE users
                    SET points = points + 25,
                        last_daily = ?
                    WHERE username = ?
                    """,
                    (int(time.time()), username)
                )
        return True

    # =========================
    # 🏅 MEDALS
    # =========================
    def add_medal(self, username: str, medal: str):
        if medal not in ("gold", "silver", "bronze"):
            return

        self.ensure_user(username)

        with _db_lock:
            with self.conn:
                self.conn.execute(
                    f"UPDATE users SET {medal} = {medal} + 1 WHERE username = ?",
                    (username,)
                )

    def get_medals(self, username: str) -> dict:
        self.ensure_user(username)
        cur = self.conn.execute(
            "SELECT gold, silver, bronze FROM users WHERE username = ?",
            (username,)
        )
        row = cur.fetchone()
        return {
            "gold": row["gold"],
            "silver": row["silver"],
            "bronze": row["bronze"],
        }


# =========================
# 🔗 SHARED DATABASE INSTANCE
# =========================
db = Database()