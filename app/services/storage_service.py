from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from app.core.config import settings
import uuid
from typing import Optional

class StorageService:
    
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """Подключение к MinIO"""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
    
    def ensure_bucket_exists(self, bucket_name: str) -> None:
        """Проверяет существование бакета, создаёт если нет"""
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
    
    async def upload_file(
        self, 
        file: UploadFile, 
        user_id: str,
        bucket: str
    ) -> dict:
        """
        Загрузка файла в MinIO с использованием потоков
        Возвращает метаданные файла
        """
        # Генерируем уникальное имя объекта
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        object_key = f"{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Получаем размер файла (из аргумента, переданного в эндпоинт)
        # Размер уже получен в files.py через seek/tell, сохраним его
        # Если size не передан, вычисляем через seek
        if hasattr(file, 'size') and file.size:
            file_size = file.size
        else:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
        
        # Загружаем файл потоково
        result = self.client.put_object(
            bucket_name=bucket,
            object_name=object_key,
            data=file.file,
            length=file_size,
            content_type=file.content_type
        )
        
        return {
            "object_key": object_key,
            "size": file_size,  
            "etag": result.etag
        }
    
    def get_file_stream(self, bucket: str, object_key: str):
        """
        Получение потока файла для скачивания
        """
        try:
            response = self.client.get_object(bucket, object_key)
            return response
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            raise
    
    def delete_file(self, bucket: str, object_key: str) -> bool:
        """
        Удаление файла из MinIO
        """
        try:
            self.client.remove_object(bucket, object_key)
            return True
        except S3Error:
            return False
    
    def file_exists(self, bucket: str, object_key: str) -> bool:
        """
        Проверка существования файла в MinIO
        """
        try:
            self.client.stat_object(bucket, object_key)
            return True
        except S3Error:
            return False

# Глобальный экземпляр
storage_service = StorageService()