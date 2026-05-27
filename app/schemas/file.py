from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FileResponse(BaseModel):
    """Ответ при загрузке файла"""
    id: str = Field(..., description="ID файла")
    original_name: str = Field(..., description="Оригинальное имя файла")
    size: int = Field(..., description="Размер файла в байтах")
    mimetype: str = Field(..., description="MIME-тип файла")
    created_at: datetime = Field(..., description="Дата загрузки")
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    """Ответ после загрузки файла"""
    file_id: str = Field(..., description="ID загруженного файла")
    message: str = Field(default="Файл успешно загружен")

class FileDownloadResponse(BaseModel):
    """Ответ при скачивании файла (метаданные)"""
    file_id: str
    original_name: str
    mimetype: str
    size: int