from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import authenticate
from app.repositories.user_repository_mongo import UserRepository
from app.repositories.file_repository_mongo import FileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.core.cache import cache_service
from datetime import datetime

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(authenticate)):
    """
    Получение профиля текущего пользователя
    """
    # Получаем пользователя из БД
    user = await UserRepository.find_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return ProfileResponse(
        id=str(user["_id"]),  # ← ИСПРАВЛЕНО: user["_id"]
        email=user["email"],  # ← ИСПРАВЛЕНО: user["email"]
        avatar_file_id=user.get("avatar_file_id"),  # ← ИСПРАВЛЕНО: user.get()
        has_avatar=user.get("avatar_file_id") is not None  # ← ИСПРАВЛЕНО
    )


@router.post("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(authenticate)
):
    """
    Обновление профиля пользователя (установка аватара)
    """
    # 1. Получаем пользователя
    user = await UserRepository.find_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # 2. Если указан avatar_file_id, проверяем, что файл существует и принадлежит пользователю
    if profile_data.avatar_file_id:
        file_meta = await FileRepository.get_by_id(profile_data.avatar_file_id)
        if not file_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл аватара не найден"
            )
        
        # Проверяем владельца файла (используем словарь)
        if file_meta["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете использовать только свои файлы для аватара"
            )
    
    # 3. Обновляем поле avatar_file_id в БД
    update_data = {
        "avatar_file_id": profile_data.avatar_file_id,
        "updated_at": datetime.utcnow()
    }
    await UserRepository.update(current_user["id"], update_data)
    
    # 4. Получаем обновлённого пользователя
    user = await UserRepository.find_by_id(current_user["id"])
    
    # 5. Инвалидируем кеш профиля
    cache_service.delete(f"wp:profile:user:{current_user['id']}")
    
    return ProfileResponse(
        id=str(user["_id"]),  # ← ИСПРАВЛЕНО
        email=user["email"],  # ← ИСПРАВЛЕНО
        avatar_file_id=user.get("avatar_file_id"),  # ← ИСПРАВЛЕНО
        has_avatar=user.get("avatar_file_id") is not None  # ← ИСПРАВЛЕНО
    )