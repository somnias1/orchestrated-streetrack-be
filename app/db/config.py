from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://localhost:5432/streetrack"
    cors_allowed_origins: str = "http://localhost:3000"
    auth0_domain: str = ""
    auth0_audience: str = ""
    auth0_issuer: str = ""

    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]
