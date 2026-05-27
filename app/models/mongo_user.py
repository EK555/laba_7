from datetime import datetime
from typing import Optional

# Модель пользователя (обычный Python класс, без Beanie)
class User:
    def __init__(self, email: str, password_hash: Optional[str] = None, 
                 yandex_id: Optional[str] = None, vk_id: Optional[str] = None,
                 avatar_file_id: Optional[str] = None):
        self.email = email
        self.password_hash = password_hash
        self.yandex_id = yandex_id
        self.vk_id = vk_id
        self.avatar_file_id = avatar_file_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.deleted_at = None

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "yandex_id": self.yandex_id,
            "vk_id": self.vk_id,
            "avatar_file_id": self.avatar_file_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }