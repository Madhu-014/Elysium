from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    cors_allowed_origins: str = "*"
    cors_allow_credentials: bool = False
    require_api_key: bool = False
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 120
    elysium_api_keys: str = "dev-key-123"
    kwh_per_1k_tokens: float = 0.0005
    grid_co2_g_per_kwh: float = 400.0
    enable_llm_compression: bool = False

    @property
    def api_keys(self) -> set[str]:
        return {k.strip() for k in self.elysium_api_keys.split(",") if k.strip()}

    @property
    def allowed_origins(self) -> list[str]:
        origins = [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]
        return origins or ["*"]


settings = Settings()
