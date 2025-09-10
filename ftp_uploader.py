"""
Модуль для загрузки мокапов на FTP сервер
"""
import ftplib
import os
import json
import tempfile
from datetime import datetime
from typing import List, Dict, Optional

class FTPUploader:
    """Класс для загрузки файлов на FTP сервер"""
    
    def __init__(self, host: str, username: str, password: str, remote_path: str = "/mockups"):
        """
        Инициализация FTP загрузчика
        
        Args:
            host: FTP хост
            username: Имя пользователя
            password: Пароль
            remote_path: Удаленная папка
        """
        self.host = host
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.web_url = f"http://{host}{remote_path}"
    
    def test_connection(self) -> bool:
        """Тестирует подключение к FTP серверу"""
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                print("✅ FTP подключение успешно")
                return True
        except Exception as e:
            print(f"❌ Ошибка FTP подключения: {e}")
            return False
    
    def create_remote_directory(self) -> bool:
        """Создает удаленную папку если не существует"""
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                # Пытаемся перейти в папку
                try:
                    ftp.cwd(self.remote_path)
                except ftplib.error_perm:
                    # Папка не существует, создаем
                    ftp.mkd(self.remote_path)
                    print(f"✅ Создана папка: {self.remote_path}")
                
                return True
        except Exception as e:
            print(f"❌ Ошибка создания папки: {e}")
            return False
    
    def upload_file(self, local_file: str, remote_file: str) -> bool:
        """
        Загружает файл на FTP сервер
        
        Args:
            local_file: Локальный путь к файлу
            remote_file: Имя файла на сервере
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                ftp.cwd(self.remote_path)
                
                with open(local_file, 'rb') as file:
                    ftp.storbinary(f'STOR {remote_file}', file)
                
                print(f"✅ Файл загружен: {remote_file}")
                return True
        except Exception as e:
            print(f"❌ Ошибка загрузки файла {remote_file}: {e}")
            return False
    
    def upload_mockup(self, image_data: bytes, metadata: Dict, description: str = "") -> Optional[str]:
        """
        Загружает мокап на FTP сервер
        
        Args:
            image_data: Данные изображения в байтах
            metadata: Метаданные мокапа
            description: Описание мокапа
            
        Returns:
            str: Имя загруженного файла или None при ошибке
        """
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            style = metadata.get("mockup_style", "unknown")
            filename = f"mockup_{timestamp}_{style}.jpg"
            
            # Загружаем изображение
            if self.upload_file(temp_file_path, filename):
                # Создаем метаданные
                metadata_file = filename.replace('.jpg', '.json')
                metadata_data = {
                    **metadata,
                    "description": description,
                    "uploaded_at": datetime.now().isoformat(),
                    "filename": filename,
                    "web_url": f"{self.web_url}/{filename}",
                    "source": "ftp_upload"
                }
                
                # Сохраняем метаданные во временный файл
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as temp_meta:
                    json.dump(metadata_data, temp_meta, ensure_ascii=False, indent=2)
                    temp_meta_path = temp_meta.name
                
                # Загружаем метаданные
                self.upload_file(temp_meta_path, metadata_file)
                
                # Удаляем временные файлы
                os.unlink(temp_file_path)
                os.unlink(temp_meta_path)
                
                return filename
            else:
                # Удаляем временный файл при ошибке
                os.unlink(temp_file_path)
                return None
                
        except Exception as e:
            print(f"❌ Ошибка загрузки мокапа: {e}")
            return None
    
    def list_files(self) -> List[Dict]:
        """
        Получает список файлов с FTP сервера
        
        Returns:
            List[Dict]: Список файлов с метаданными
        """
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                ftp.cwd(self.remote_path)
                
                files = []
                ftp.retrlines('LIST', files.append)
                
                mockups = []
                for file_info in files:
                    parts = file_info.split()
                    if len(parts) >= 9:
                        filename = parts[-1]
                        if filename.endswith('.jpg'):
                            # Ищем соответствующий JSON файл
                            json_filename = filename.replace('.jpg', '.json')
                            
                            # Загружаем метаданные
                            metadata = {}
                            try:
                                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                                    ftp.retrbinary(f'RETR {json_filename}', temp_file.write)
                                
                                with open(temp_file.name, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                
                                os.unlink(temp_file.name)
                            except:
                                pass
                            
                            mockups.append({
                                'filename': filename,
                                'web_url': f"{self.web_url}/{filename}",
                                'metadata': metadata,
                                'source': 'ftp_upload'
                            })
                
                return mockups
                
        except Exception as e:
            print(f"❌ Ошибка получения списка файлов: {e}")
            return []
    
    def delete_file(self, filename: str) -> bool:
        """
        Удаляет файл с FTP сервера
        
        Args:
            filename: Имя файла для удаления
            
        Returns:
            bool: True если удаление успешно
        """
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                ftp.cwd(self.remote_path)
                
                # Удаляем изображение
                ftp.delete(filename)
                
                # Удаляем метаданные
                json_filename = filename.replace('.jpg', '.json')
                try:
                    ftp.delete(json_filename)
                except:
                    pass
                
                print(f"✅ Файл удален: {filename}")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка удаления файла {filename}: {e}")
            return False

def get_ftp_uploader() -> Optional[FTPUploader]:
    """
    Получает настроенный FTP загрузчик
    
    Returns:
        FTPUploader: Настроенный загрузчик или None
    """
    try:
        from config import FTP_HOST, FTP_USERNAME, FTP_PASSWORD, FTP_REMOTE_PATH
        
        # Проверяем, что все настройки заполнены
        if not FTP_HOST or not FTP_USERNAME or not FTP_PASSWORD:
            print("❌ FTP настройки не заполнены. Добавьте в .env:")
            print("   FTP_HOST=your_ftp_host")
            print("   FTP_USERNAME=your_username")
            print("   FTP_PASSWORD=your_password")
            return None
        
        uploader = FTPUploader(FTP_HOST, FTP_USERNAME, FTP_PASSWORD, FTP_REMOTE_PATH)
        
        # Тестируем подключение
        if uploader.test_connection():
            uploader.create_remote_directory()
            return uploader
        else:
            return None
            
    except Exception as e:
        print(f"❌ Ошибка инициализации FTP загрузчика: {e}")
        return None
