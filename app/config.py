from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    ids_file_name: str
    links_file_name: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore[call-arg]
