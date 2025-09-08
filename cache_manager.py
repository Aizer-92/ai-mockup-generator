"""
Система кэширования для экономии API вызовов
"""
import os
import json
import time
import hashlib
from typing import Optional, Dict, Any
from PIL import Image
import io
from config import CACHE_DIR, CACHE_ENABLED, CACHE_EXPIRY_HOURS

class CacheManager:
    def __init__(self):
        """Инициализация менеджера кэша"""
        self.cache_dir = CACHE_DIR
        self.enabled = CACHE_ENABLED
        self.expiry_hours = CACHE_EXPIRY_HOURS
        
        if self.enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def generate_cache_key(self, product_hash: str, logo_hash: str, 
                          style: str, additional_params: Dict = None) -> str:
        """Генерация ключа кэша"""
        params_str = ""
        if additional_params:
            params_str = json.dumps(additional_params, sort_keys=True)
        
        key_string = f"{product_hash}_{logo_hash}_{style}_{params_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def is_cached(self, cache_key: str) -> bool:
        """Проверка наличия в кэше"""
        if not self.enabled:
            return False
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if not os.path.exists(cache_file):
            return False
        
        # Проверка времени создания
        file_time = os.path.getctime(cache_file)
        current_time = time.time()
        expiry_seconds = self.expiry_hours * 3600
        
        return (current_time - file_time) < expiry_seconds
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Получение результата из кэша"""
        if not self.enabled or not self.is_cached(cache_key):
            return None
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения кэша: {e}")
            return None
    
    def save_to_cache(self, cache_key: str, result: Dict) -> bool:
        """Сохранение результата в кэш"""
        if not self.enabled:
            return False
        
        try:
            # Убеждаемся, что папка кэша существует
            os.makedirs(self.cache_dir, exist_ok=True)
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Добавление метаданных
            cache_data = {
                "timestamp": time.time(),
                "expiry_hours": self.expiry_hours,
                "result": result
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения в кэш: {e}")
            return False
    
    def save_image_to_cache(self, cache_key: str, image: Image.Image, 
                           image_name: str) -> Optional[str]:
        """Сохранение изображения в кэш"""
        if not self.enabled:
            return None
        
        try:
            image_dir = os.path.join(self.cache_dir, "images")
            os.makedirs(image_dir, exist_ok=True)
            
            image_path = os.path.join(image_dir, f"{cache_key}_{image_name}.jpg")
            image.save(image_path, "JPEG", quality=95)
            
            return image_path
        except Exception as e:
            print(f"Ошибка сохранения изображения в кэш: {e}")
            return None
    
    def get_cache_stats(self) -> Dict:
        """Получение статистики кэша"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) 
                          if f.endswith('.json')]
            
            total_size = 0
            for file in cache_files:
                file_path = os.path.join(self.cache_dir, file)
                total_size += os.path.getsize(file_path)
            
            return {
                "enabled": True,
                "total_files": len(cache_files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "cache_dir": self.cache_dir
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    def clear_expired_cache(self) -> int:
        """Очистка устаревшего кэша"""
        if not self.enabled:
            return 0
        
        cleared_count = 0
        current_time = time.time()
        expiry_seconds = self.expiry_hours * 3600
        
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file)
                    file_time = os.path.getctime(file_path)
                    
                    if (current_time - file_time) > expiry_seconds:
                        os.remove(file_path)
                        cleared_count += 1
        except Exception as e:
            print(f"Ошибка очистки кэша: {e}")
        
        return cleared_count
    
    def clear_all_cache(self) -> bool:
        """Полная очистка кэша"""
        if not self.enabled:
            return False
        
        try:
            for file in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
            return True
        except Exception as e:
            print(f"Ошибка полной очистки кэша: {e}")
            return False
