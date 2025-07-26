import aiohttp

from todoist_api_python.authentication import get_authentication_url, revoke_auth_token_async
from config.core import Config


class TodoistAuth:
    scopes = ["data:read", "task:add", "data:delete"]

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_auth_url(self, state: str) -> str:
        return get_authentication_url(
            client_id=self.client_id,
            scopes=self.scopes,
            state=state,

        )

    async def get_access_token(self, code: str) -> dict:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://todoist.com/oauth/access_token", data=data) as response:
                response.raise_for_status()
                return await response.json()

    async def reveal_access_token(self, token: str) -> bool:
        return await revoke_auth_token_async(self.client_id, self.client_secret, token)


todoist_auth = TodoistAuth(
    client_id=Config.TODOIST_CLIENT_ID,
    client_secret=Config.TODOIST_CLIENT_SECRET,
)
