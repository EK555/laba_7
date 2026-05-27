from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, description="Пароль (мин. 6 символов)")

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")

class TokenResponse(BaseModel):
    """Схема ответа с токенами"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Тип токена")
    user: dict = Field(..., description="Данные пользователя")

class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: str = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    avatar_file_id: Optional[str] = Field(None, description="ID аватара")