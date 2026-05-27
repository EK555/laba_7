from fastapi import Request, HTTPException
from app.services.auth_service import AuthService
from app.utils.jwt_utils import verify_access_token
from app.core.cache import cache_service

async def authenticate(request: Request):
    """Middleware аутентификации"""
    access_token = request.cookies.get('access_token')
    
    print(f"[DEBUG] access_token from cookie: {access_token[:50] if access_token else 'None'}...")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Не предоставлен access token")
    
    # 1. Проверяем подпись JWT
    payload = verify_access_token(access_token)
    print(f"[DEBUG] payload: {payload}")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")
    
    # 2. Проверяем JTI в Redis (отозван ли токен)
    jti = payload.get('jti')
    user_id = payload.get('sub')
    print(f"[DEBUG] user_id from payload: {user_id}")
    
    if jti and cache_service.is_available():
        cache_key = f"wp:auth:user:{user_id}:access:{jti}"
        if not cache_service.get(cache_key):
            raise HTTPException(status_code=401, detail="Токен отозван")
    
    # 3. Получаем пользователя по ID из токена
    user = await AuthService.get_user_by_id(user_id)
    print(f"[DEBUG] user from DB: {user}")
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # 4. Возвращаем словарь
    request.state.user = user
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "avatar_file_id": user.get("avatar_file_id")
    }