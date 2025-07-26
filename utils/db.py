import aiosqlite
from typing import Optional
from dataclasses import dataclass
from config.core import Config


@dataclass
class UserToken:
    user_id: str
    access_token: str


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    access_token TEXT NOT NULL
                )
            """)
            await db.commit()

    async def save_token(self, user_id: int, access_token: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO user_tokens (user_id, access_token) VALUES (?, ?)",
                (user_id, access_token)
            )
            await db.commit()

    async def get_token(self, user_id: int) -> Optional[UserToken]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id, access_token FROM user_tokens WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return UserToken(*row)

    async def reveal_token(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM user_tokens WHERE user_id = ?", (user_id,))
            await db.commit()


db = Database(Config.DB_PATH)
