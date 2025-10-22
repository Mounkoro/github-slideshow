from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "Bank Manager API"
    secret_key: str = Field(default="change-this-secret", description="JWT secret")
    access_token_expire_minutes: int = 60
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_db: str = "bankdb"
    bcrypt_rounds: int = 12
    brute_force_window_seconds: int = 900
    brute_force_max_attempts: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
