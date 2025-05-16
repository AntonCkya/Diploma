from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "auth"

    @property
    def DATABASE_URL(self):
        DB_HOST = self.DB_HOST
        DB_PORT = self.DB_PORT
        DB_USER = self.DB_USER
        DB_PASSWORD = self.DB_PASSWORD
        DB_NAME = self.DB_NAME
        return f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    AUTH_PATH: str = "http://localhost:8001"
    SAMPLE_PATH: str = "http://localhost:8002"

    class Config:
        env_file = ".env"

settings = Settings()
