from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    S3_BUCKET: str
    S3_ENDPOINT_URL: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str

    class Config:
        env_file = ".env"

settings = Settings()
