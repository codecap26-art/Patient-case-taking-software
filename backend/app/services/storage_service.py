import os
import uuid
import shutil
from typing import Tuple
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import ValidationException
from app.utils.validators import sanitize_filename


class StorageService:
    def __init__(self, base_path: str = settings.STORAGE_PATH):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(self, upload_file: UploadFile, subfolder: str = "documents") -> Tuple[str, str, int, str]:
        """
        Saves uploaded file securely.
        Returns (storage_key, sanitized_filename, file_size_bytes, formatted_size_str)
        """
        filename = sanitize_filename(upload_file.filename or "uploaded_file.dat")
        content_type = upload_file.content_type or "application/octet-stream"

        if content_type not in settings.ALLOWED_MIME_TYPES and not upload_file.filename.endswith((".pdf", ".jpg", ".png", ".txt")):
            raise ValidationException(f"Unsupported file type: {content_type}. Allowed types: PDF, JPG, PNG, TXT.")

        unique_id = str(uuid.uuid4())
        dest_dir = os.path.join(self.base_path, subfolder)
        os.makedirs(dest_dir, exist_ok=True)

        storage_key = f"{subfolder}/{unique_id}_{filename}"
        dest_path = os.path.join(self.base_path, storage_key)

        file_size = 0
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            file_size = buffer.tell()

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            os.remove(dest_path)
            raise ValidationException(f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB} MB")

        # Format display size
        if file_size < 1024 * 1024:
            display_size = f"{file_size / 1024:.1f} KB"
        else:
            display_size = f"{file_size / (1024 * 1024):.1f} MB"

        return storage_key, filename, file_size, display_size

    def get_file_path(self, storage_key: str) -> str:
        return os.path.join(self.base_path, storage_key)

    def delete_file(self, storage_key: str) -> bool:
        path = self.get_file_path(storage_key)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
