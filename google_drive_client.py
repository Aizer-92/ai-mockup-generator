"""
Модуль для работы с Google Drive API
Позволяет загружать и получать мокапы из Google Drive
"""
import os
import io
import json
import base64
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from PIL import Image

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
except ImportError:
    print("Google Drive API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class GoogleDriveClient:
    """Клиент для работы с Google Drive API"""
    
    # Области доступа для Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, credentials_file: str = None, token_file: str = None):
        """
        Инициализация клиента Google Drive
        
        Args:
            credentials_file: Путь к файлу с учетными данными OAuth
            token_file: Путь к файлу с токеном доступа
        """
        self.credentials_file = credentials_file or 'credentials.json'
        self.token_file = token_file or 'token.json'
        self.service = None
        self.folder_id = None
        
    def authenticate(self) -> bool:
        """
        Аутентификация в Google Drive API
        
        Returns:
            bool: True если аутентификация успешна
        """
        try:
            creds = None
            
            # Проверяем существующий токен
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # Если нет валидных учетных данных, запрашиваем авторизацию
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        print(f"Файл {self.credentials_file} не найден!")
                        print("Скачайте файл credentials.json из Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Сохраняем учетные данные для следующего запуска
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Создаем сервис Google Drive
            self.service = build('drive', 'v3', credentials=creds)
            return True
            
        except Exception as e:
            print(f"Ошибка аутентификации Google Drive: {e}")
            return False
    
    def create_mockups_folder(self, folder_name: str = "AI Mockup Generator") -> Optional[str]:
        """
        Создает папку для мокапов в Google Drive
        
        Args:
            folder_name: Название папки
            
        Returns:
            str: ID созданной папки или None при ошибке
        """
        try:
            if not self.service:
                return None
            
            # Проверяем, существует ли уже папка
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                self.folder_id = files[0]['id']
                print(f"Найдена существующая папка: {folder_name}")
                return self.folder_id
            
            # Создаем новую папку
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            self.folder_id = folder.get('id')
            print(f"Создана папка: {folder_name} (ID: {self.folder_id})")
            return self.folder_id
            
        except Exception as e:
            print(f"Ошибка создания папки: {e}")
            return None
    
    def upload_mockup(self, image_data: bytes, filename: str, metadata: Dict = None) -> Optional[str]:
        """
        Загружает мокап в Google Drive
        
        Args:
            image_data: Данные изображения в байтах
            filename: Имя файла
            metadata: Метаданные мокапа
            
        Returns:
            str: ID загруженного файла или None при ошибке
        """
        try:
            if not self.service or not self.folder_id:
                return None
            
            # Создаем метаданные файла
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            # Если есть метаданные, сохраняем их в описании
            if metadata:
                description = json.dumps(metadata, ensure_ascii=False, indent=2)
                file_metadata['description'] = description
            
            # Создаем медиа-объект для загрузки
            media = MediaIoBaseUpload(
                io.BytesIO(image_data),
                mimetype='image/jpeg',
                resumable=True
            )
            
            # Загружаем файл
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,createdTime,description'
            ).execute()
            
            print(f"Загружен файл: {filename} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            print(f"Ошибка загрузки файла {filename}: {e}")
            return None
    
    def get_mockups_list(self, limit: int = 50) -> List[Dict]:
        """
        Получает список мокапов из Google Drive
        
        Args:
            limit: Максимальное количество файлов
            
        Returns:
            List[Dict]: Список мокапов с метаданными
        """
        try:
            if not self.service or not self.folder_id:
                return []
            
            # Запрашиваем файлы из папки
            query = f"'{self.folder_id}' in parents and mimeType='image/jpeg' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id,name,createdTime,description,size)",
                orderBy="createdTime desc",
                pageSize=limit
            ).execute()
            
            files = results.get('files', [])
            mockups = []
            
            for file in files:
                mockup_data = {
                    'id': file.get('id'),
                    'filename': file.get('name'),
                    'created_time': file.get('createdTime'),
                    'size': file.get('size'),
                    'metadata': {}
                }
                
                # Парсим метаданные из описания
                description = file.get('description', '')
                if description:
                    try:
                        mockup_data['metadata'] = json.loads(description)
                    except json.JSONDecodeError:
                        pass
                
                mockups.append(mockup_data)
            
            return mockups
            
        except Exception as e:
            print(f"Ошибка получения списка файлов: {e}")
            return []
    
    def download_mockup(self, file_id: str) -> Optional[bytes]:
        """
        Скачивает мокап из Google Drive
        
        Args:
            file_id: ID файла в Google Drive
            
        Returns:
            bytes: Данные изображения или None при ошибке
        """
        try:
            if not self.service:
                return None
            
            # Скачиваем файл
            request = self.service.files().get_media(fileId=file_id)
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return file_data.getvalue()
            
        except Exception as e:
            print(f"Ошибка скачивания файла {file_id}: {e}")
            return None
    
    def delete_mockup(self, file_id: str) -> bool:
        """
        Удаляет мокап из Google Drive
        
        Args:
            file_id: ID файла в Google Drive
            
        Returns:
            bool: True если удаление успешно
        """
        try:
            if not self.service:
                return False
            
            self.service.files().delete(fileId=file_id).execute()
            print(f"Удален файл: {file_id}")
            return True
            
        except Exception as e:
            print(f"Ошибка удаления файла {file_id}: {e}")
            return False
    
    def get_drive_info(self) -> Dict:
        """
        Получает информацию о Google Drive
        
        Returns:
            Dict: Информация о диске
        """
        try:
            if not self.service:
                return {}
            
            about = self.service.about().get(fields="user,storageQuota").execute()
            
            return {
                'user': about.get('user', {}).get('displayName', 'Unknown'),
                'email': about.get('user', {}).get('emailAddress', 'Unknown'),
                'storage_used': about.get('storageQuota', {}).get('used', '0'),
                'storage_limit': about.get('storageQuota', {}).get('limit', '0'),
                'folder_id': self.folder_id
            }
            
        except Exception as e:
            print(f"Ошибка получения информации о диске: {e}")
            return {}

def get_drive_client() -> Optional[GoogleDriveClient]:
    """
    Получает настроенный клиент Google Drive
    
    Returns:
        GoogleDriveClient: Настроенный клиент или None
    """
    try:
        client = GoogleDriveClient()
        if client.authenticate():
            client.create_mockups_folder()
            return client
        return None
    except Exception as e:
        print(f"Ошибка инициализации Google Drive клиента: {e}")
        return None
