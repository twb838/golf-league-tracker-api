from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "3306"
    DATABASE_USER: str = "twb838"
    DATABASE_PASSWORD: str = "Punter11"
    DATABASE_NAME: str = "leaguetracker"
    
    class Config:
        env_file = ".env"

settings = Settings()