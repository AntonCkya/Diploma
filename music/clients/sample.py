import httpx
from fastapi import UploadFile

from config import settings

class PreprocessingClient:
    def __init__(self):
        self.base_url = settings.SAMPLE_PATH
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def upload_audio(self, file: UploadFile) -> dict:
        try:
            response = await self.client.post(
                "/sample/upload",
                files={"file": (file.filename, file.file, "audio/mpeg")}
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            return None
