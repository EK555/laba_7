from fastapi import APIRouter, HTTPException, status, Response
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Регистрация нового пользователя"""
    try:
        user = await AuthService.register(user_data.email, user_data.password)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(user_data: UserLogin, response: Response):
    """Авторизация пользователя"""
    try:
        access_token, refresh_token, user = await AuthService.login(
            user_data.email, 
            user_data.password
        )
        
        # Устанавливаем ОБА токена в cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 60  # 15 минут
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 дней
        )
        
        return {
            "message": "Вход выполнен успешно",
            "user": user
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )