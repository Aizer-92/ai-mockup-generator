"""
Модуль для хранения мокапов на сервере
Простая альтернатива Google Drive
"""
import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional
from PIL import Image
import io

class ServerStorage:
    """Класс для хранения мокапов на сервере"""
    
    def __init__(self, storage_path: str = None, web_url: str = None):
        """
        Инициализация хранилища
        
        Args:
            storage_path: Путь к папке для хранения файлов
            web_url: URL для доступа к файлам через веб
        """
        self.storage_path = storage_path or '/tmp/mockups'
        self.web_url = web_url or 'http://localhost:8501/static/mockups'
        
        # Создаем папку если не существует
        os.makedirs(self.storage_path, exist_ok=True)
    
    def save_mockup(self, image_data: bytes, metadata: Dict, description: str = "") -> Optional[str]:
        """
        Сохраняет мокап на сервер
        
        Args:
            image_data: Данные изображения в байтах
            metadata: Метаданные мокапа
            description: Описание мокапа
            
        Returns:
            str: Имя сохраненного файла или None при ошибке
        """
        try:
            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            style = metadata.get("mockup_style", "unknown")
            filename = f"mockup_{timestamp}_{style}.jpg"
            
            # Сохраняем изображение
            filepath = os.path.join(self.storage_path, filename)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Подготавливаем метаданные для сохранения
            save_metadata = {
                **metadata,
                "description": description,
                "saved_at": datetime.now().isoformat(),
                "filename": filename,
                "filepath": filepath,
                "web_url": f"{self.web_url}/{filename}",
                "source": "server_storage"
            }
            
            # Сохраняем метаданные
            metadata_file = filepath.replace('.jpg', '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(save_metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Мокап сохранен на сервер: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка сохранения на сервер: {e}")
            return None
    
    def get_mockups_list(self, limit: int = 50) -> List[Dict]:
        """
        Получает список мокапов с сервера
        
        Args:
            limit: Максимальное количество файлов
            
        Returns:
            List[Dict]: Список мокапов с метаданными
        """
        try:
            mockups = []
            
            if not os.path.exists(self.storage_path):
                return mockups
            
            # Получаем все файлы изображений
            files = [f for f in os.listdir(self.storage_path) if f.endswith('.jpg')]
            files.sort(key=lambda x: os.path.getctime(os.path.join(self.storage_path, x)), reverse=True)
            
            for filename in files[:limit]:
                filepath = os.path.join(self.storage_path, filename)
                metadata_file = filepath.replace('.jpg', '.json')
                
                # Загружаем метаданные
                metadata = {}
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except:
                        pass
                
                # Читаем изображение для base64
                try:
                    with open(filepath, 'rb') as f:
                        image_data = f.read()
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                except:
                    image_base64 = None
                
                mockups.append({
                    'id': filename.replace('.jpg', ''),
                    'filename': filename,
                    'filepath': filepath,
                    'web_url': f"{self.web_url}/{filename}",
                    'metadata': metadata,
                    'created_time': os.path.getctime(filepath),
                    'source': 'server_storage',
                    'image_data': image_base64
                })
            
            return mockups
            
        except Exception as e:
            print(f"❌ Ошибка получения списка мокапов: {e}")
            return []
    
    def get_mockup(self, filename: str) -> Optional[bytes]:
        """
        Получает мокап с сервера
        
        Args:
            filename: Имя файла
            
        Returns:
            bytes: Данные изображения или None при ошибке
        """
        try:
            filepath = os.path.join(self.storage_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"❌ Ошибка получения мокапа {filename}: {e}")
            return None
    
    def delete_mockup(self, filename: str) -> bool:
        """
        Удаляет мокап с сервера
        
        Args:
            filename: Имя файла
            
        Returns:
            bool: True если удаление успешно
        """
        try:
            filepath = os.path.join(self.storage_path, filename)
            metadata_file = filepath.replace('.jpg', '.json')
            
            # Удаляем файл изображения
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Удаляем файл метаданных
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            
            print(f"✅ Мокап удален с сервера: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка удаления мокапа {filename}: {e}")
            return False
    
    def get_storage_info(self) -> Dict:
        """
        Получает информацию о хранилище
        
        Returns:
            Dict: Информация о хранилище
        """
        try:
            if not os.path.exists(self.storage_path):
                return {
                    'path': self.storage_path,
                    'exists': False,
                    'file_count': 0,
                    'total_size': 0
                }
            
            files = os.listdir(self.storage_path)
            image_files = [f for f in files if f.endswith('.jpg')]
            
            total_size = 0
            for filename in image_files:
                filepath = os.path.join(self.storage_path, filename)
                total_size += os.path.getsize(filepath)
            
            return {
                'path': self.storage_path,
                'exists': True,
                'file_count': len(image_files),
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'web_url': self.web_url
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения информации о хранилище: {e}")
            return {}

def get_server_storage() -> ServerStorage:
    """
    Получает настроенное хранилище сервера
    
    Returns:
        ServerStorage: Настроенное хранилище
    """
    from config import get_config
    config = get_config()
    
    storage_path = config.get('SERVER_STORAGE_PATH', '/tmp/mockups')
    web_url = config.get('SERVER_WEB_URL', 'http://localhost:8501/static/mockups')
    
    return ServerStorage(storage_path, web_url)
