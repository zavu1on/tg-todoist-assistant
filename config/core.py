import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    TODOIST_CLIENT_ID = os.getenv("TODOIST_CLIENT_ID")
    TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")
    DB_PATH = os.getenv("DB_PATH", "todoist.db")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    MODEL = os.getenv("MODEL", "qwen/qwen-2.5-72b-instruct:free")

    @classmethod
    def validate(cls):
        required_variables = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "TODOIST_CLIENT_ID": cls.TODOIST_CLIENT_ID,
            "TODOIST_CLIENT_SECRET": cls.TODOIST_CLIENT_SECRET,
            "OPENROUTER_API_KEY": cls.OPENROUTER_API_KEY
        }

        for variable, value in required_variables.items():
            if not value:
                raise ValueError(f"{variable} not found in .env file")
