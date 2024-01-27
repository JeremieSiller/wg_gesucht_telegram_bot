from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    kleinanzeigen_url: str
    ids_file_name: str


settings = Settings()  # type: ignore[call-arg]
