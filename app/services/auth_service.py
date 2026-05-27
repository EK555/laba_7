from app.repositories.user_repository_mongo import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from datetime import datetime
from jose import jwt
from app.core.config import settings

class AuthService:
    
    @staticmethod
    async def register(email: str, password: str):
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь
        existing = await UserRepository.find_by_email(email)
        if existing:
            raise ValueError("Пользователь с таким email уже существует")
        
        # Хешируем пароль и создаём пользователя
        password_hash = hash_password(password)
        user = await UserRepository.create(email, password_hash)
        
        return {
            "id": user["_id"],
            "email": user["email"]
        }
    
    @staticmethod
    async def login(email: str, password: str):
        """Авторизация пользователя"""
        # Ищем пользователя по email
        user = await UserRepository.find_by_email(email)
        
        # Проверяем существование пользователя
        if not user:
            raise ValueError("Неверный email или пароль")
        
        # Проверяем пароль
        if not user.get("password_hash"):
            raise ValueError("Неверный email или пароль")
        
        if not verify_password(password, user["password_hash"]):
            raise ValueError("Неверный email или пароль")
        
        # Создаём токены
        access_token = create_access_token(
            data={"sub": user["_id"], "email": user["email"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": user["_id"]}
        )
        
        return access_token, refresh_token, {
            "id": user["_id"],
            "email": user["email"]
        }
    
    @staticmethod
    async def get_user_by_id(user_id: str):
        """Получение пользователя по ID"""
        print(f"[DEBUG] get_user_by_id called with: {user_id}")
        result = await UserRepository.find_by_id(user_id)
        print(f"[DEBUG] repository result: {result}")
        return result