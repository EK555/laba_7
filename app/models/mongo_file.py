from datetime import datetime
from typing import Optional

# Модель для метаданных файла (обычный Python класс, без Beanie)
class FileMetadata:
    def __init__(self, user_id: str, original_name: str, object_key: str, 
                 size: int, mimetype: str, bucket: str):
        self.user_id = user_id
        self.original_name = original_name
        self.object_key = object_key
        self.size = size
        self.mimetype = mimetype
        self.bucket = bucket
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.deleted_at = None

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения в MongoDB"""
        return {
            "user_id": self.user_id,
            "original_name": self.original_name,
            "object_key": self.object_key,
            "size": self.size,
            "mimetype": self.mimetype,
            "bucket": self.bucket,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }