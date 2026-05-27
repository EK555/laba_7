from datetime import datetime
from typing import Optional

# Модель услуги (обычный Python класс, без Beanie)
class Service:
    def __init__(self, name: str, description: str, duration: int, 
                 price: float, category: str, user_id: Optional[str] = None):
        self.name = name
        self.description = description
        self.duration = duration
        self.price = price
        self.category = category
        self.user_id = user_id
        self.status = "active"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.deleted_at = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "price": self.price,
            "category": self.category,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at
        }