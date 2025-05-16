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

    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()
