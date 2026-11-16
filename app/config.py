"""
Application settings.

Values are read from environment variables, or from the .env file
in the project root. This keeps secrets (like the database password)
out of the source code.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Each attribute maps to an environment variable with the same name
    # (case-insensitive). Example: DATABASE_URL in .env -> settings.database_url
    app_name: str = "API Key and Usage Metering Service"
    database_url: str  # no default: the app refuses to start if it's missing

    # Tell pydantic-settings to also read values from the .env file
    model_config = SettingsConfigDict(env_file=".env")


# Create one shared settings object that the rest of the app imports
settings = Settings()
