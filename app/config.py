from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiV1Config(BaseModel):
    prefix: str = "/v1"


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

    prefix: str = "/api"
    v1: ApiV1Config = ApiV1Config()


class DatabaseConfig(BaseModel):
    name: str
    user: str
    password: str

    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.example", ".env"),
        env_prefix="APP__",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    api: ApiConfig = ApiConfig()
    db: DatabaseConfig


settings = Settings()
