from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # postgresql
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # jwt
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # white list endpoints without lodin
    EXCLUDED_PATHS: list[str]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings() # type: ignore