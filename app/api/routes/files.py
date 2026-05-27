from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from fastapi.responses import StreamingResponse
from app.middleware.auth import authenticate
from app.services.storage_service import storage_service
from app.repositories.file_repository_mongo import FileRepository
from app.schemas.file import FileUploadResponse
from app.core.config import settings
from app.core.cache import cache_service

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    current_user: dict = Depends(authenticate)
):
    """
    Загрузка файла в MinIO
    - Поддерживаемые типы: image/jpeg, image/png, image/jpg
    - Максимальный размер: 10 MB
    """
    # 1. Валидация типа файла
    allowed_mimetypes = ["image/jpeg", "image/png", "image/jpg"]
    if not file.content_type or file.content_type not in allowed_mimetypes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(allowed_mimetypes)}"
        )
    
    # 2. Получаем размер файла БЕЗ чтения в память
    file.file.seek(0, 2)  # перемещаемся в конец файла
    file_size = file.file.tell()  # получаем позицию = размер
    file.file.seek(0)  # возвращаемся в начало
    
    # 3. Валидация размера
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {settings.MAX_FILE_SIZE // (1024*1024)} MB"
        )
    
    # 4. Загружаем файл в MinIO (потоково)
    upload_result = await storage_service.upload_file(
        file=file,
        user_id=current_user["id"],
        bucket=settings.MINIO_BUCKET
    )
    
    # 5. Сохраняем метаданные в MongoDB
    file_data = {
        "user_id": current_user["id"],
        "original_name": file.filename,
        "object_key": upload_result["object_key"],
        "size": upload_result["size"],
        "mimetype": file.content_type,
        "bucket": settings.MINIO_BUCKET
    }
    db_file = await FileRepository.create(file_data)
    
    return FileUploadResponse(file_id=str(db_file["_id"]))


@router.get("/{file_id}")
async def download_file(
    file_id: str,
    current_user: dict = Depends(authenticate)
):
    """
    Скачивание файла по ID
    - Доступ только владельцу файла
    """
    # 1. Пытаемся получить метаданные из кеша
    cache_key = f"wp:files:{file_id}:meta"
    cached_meta = cache_service.get(cache_key)
    
    if cached_meta:
        file_meta = cached_meta
    else:
        # 2. Получаем метаданные файла из БД
        file_meta_db = await FileRepository.get_by_id(file_id)
        if not file_meta_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
        # Сохраняем в кеш
        file_meta = {
            "user_id": file_meta_db["user_id"],           
            "bucket": file_meta_db["bucket"],             
            "object_key": file_meta_db["object_key"],     
            "mimetype": file_meta_db["mimetype"],         
            "size": file_meta_db["size"],                 
            "original_name": file_meta_db["original_name"] 
        }
        cache_service.set(cache_key, file_meta, ttl=300)
    
    # 3. Проверяем права доступа
    if file_meta["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому файлу"
        )
    
    # 4. Получаем поток файла из MinIO
    file_stream = storage_service.get_file_stream(
        bucket=file_meta["bucket"],
        object_key=file_meta["object_key"]
    )
    
    if not file_stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден в хранилище"
        )
    
    # 5. Возвращаем файл с правильными заголовками
    return StreamingResponse(
        file_stream,
        media_type=file_meta["mimetype"],
        headers={
            "Content-Disposition": f'attachment; filename="{file_meta["original_name"]}"',
            "Content-Length": str(file_meta["size"])
        }
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    current_user: dict = Depends(authenticate)
):
    """
    Удаление файла (soft delete + удаление из MinIO)
    """
    # 1. Получаем метаданные файла из БД
    file_meta = await FileRepository.get_by_id(file_id)
    if not file_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден"
        )
    
    # 2. Проверяем права доступа
    if file_meta["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому файлу"
        )
    
    # 3. Удаляем файл из MinIO
    storage_service.delete_file(file_meta["bucket"], file_meta["object_key"])
    
    # 4. Делаем soft delete в БД
    await FileRepository.soft_delete(file_id)
    
    # 5. Удаляем из кеша
    cache_service.delete(f"wp:files:{file_id}:meta")
    
    return None