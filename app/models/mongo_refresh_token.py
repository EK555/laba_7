from datetime import datetime
from typing import Optional

class RefreshToken:
    def __init__(self, user_id: str, token_hash: str, expires_at: datetime):
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked = False
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "token_hash": self.token_hash,
            "expires_at": self.expires_at,
            "revoked": self.revoked,
            "created_at": self.created_at
        }