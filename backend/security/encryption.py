from cryptography.fernet import Fernet
import base64
import os
from typing import Union
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EncryptionManager:
    def __init__(self):
        # Load or generate encryption key
        self.key = self._get_or_create_encryption_key()
        self.cipher = Fernet(base64.urlsafe_b64encode(self.key.encode()[:32]))

    def _get_or_create_encryption_key(self) -> str:
        """Get encryption key from environment or generate a new one"""
        key = os.getenv('ENCRYPTION_KEY')
        
        if not key:
            logger.warning("ENCRYPTION_KEY not found in environment, generating new key")
            key = self.generate_key()
            self._save_key_to_env(key)
            
        if len(key) < 32:
            raise ValueError("ENCRYPTION_KEY must be at least 32 characters")
            
        return key

    @staticmethod
    def _save_key_to_env(key: str):
        """Save generated key to .env file"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        with open(env_path, 'a') as f:
            f.write(f"\n# Auto-generated encryption key\nENCRYPTION_KEY={key}\n")
        logger.info(f"Saved new encryption key to {env_path}")

    def encrypt(self, data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()

# Initialize encryption manager
encryption_manager = EncryptionManager()
