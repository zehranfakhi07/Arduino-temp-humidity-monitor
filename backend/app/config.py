from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import base64
import os
import secrets
from pydantic import Field


class Settings(BaseSettings):
	app_name: str = "HealthShare Platform"
	debug: bool = False

	# Security
	jwt_secret: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
	jwt_algorithm: str = "HS256"
	jwt_exp_hours: int = 12

	# AES-GCM 256 key for field encryption (32 bytes base64 encoded)
	encryption_key_b64: str = Field(default_factory=lambda: base64.b64encode(os.urandom(32)).decode())

	# CORS (string URLs or "*")
	backend_cors_origins: List[str] = []

	# Database
	database_url: str = "sqlite:///./app.db"

	@field_validator("encryption_key_b64")
	@classmethod
	def validate_key_len(cls, v: str) -> str:
		try:
			key = base64.b64decode(v)
		except Exception as exc:
			raise ValueError("Invalid base64 for encryption_key_b64") from exc
		if len(key) != 32:
			raise ValueError("encryption_key_b64 must decode to 32 bytes (256-bit key)")
		return v

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()