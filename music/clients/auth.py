import httpx
from typing import Optional

from config import settings

class AuthClient:
    def __init__(self):
        self.base_url = settings.AUTH_PATH
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def validate_token(self, token: str) -> Optional[dict]:
        try:
            response = await self.client.post(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return None

    async def register(self, body) -> Optional[dict]:
        try:
            response = await self.client.post(
                "/auth/register",
                json=body
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return None
