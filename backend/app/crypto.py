import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .config import settings


def _get_key() -> bytes:
	return base64.b64decode(settings.encryption_key_b64)


def encrypt_string(plaintext: str) -> str:
	if plaintext is None:
		return None
	key = _get_key()
	aesgcm = AESGCM(key)
	nonce = os.urandom(12)
	ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
	return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_string(encoded: str) -> str:
	if encoded is None:
		return None
	data = base64.b64decode(encoded)
	nonce = data[:12]
	ciphertext = data[12:]
	key = _get_key()
	aesgcm = AESGCM(key)
	plaintext = aesgcm.decrypt(nonce, ciphertext, None)
	return plaintext.decode("utf-8")