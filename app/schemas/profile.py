from pydantic import BaseModel, Field
from typing import Optional

class ProfileResponse(BaseModel):
    """Ответ с данными профиля пользователя"""
    id: str = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    avatar_file_id: Optional[str] = Field(None, description="ID аватара")
    has_avatar: bool = Field(False, description="Есть ли аватар")

class ProfileUpdateRequest(BaseModel):
    """Запрос на обновление профиля"""
    avatar_file_id: Optional[str] = Field(None, description="ID файла аватара")