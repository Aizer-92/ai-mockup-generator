"""
Основной модуль генерации мокапов
Объединяет все компоненты для создания финальных мокапов
"""
import os
import time
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io
import base64

from gemini_client import GeminiClient
from image_processor import ImageProcessor
from cache_manager import CacheManager
from config import OUTPUT_DIR, BATCH_SIZE

class MockupGenerator:
    def __init__(self):
        """Инициализация генератора мокапов"""
        self.gemini_client = GeminiClient()
        self.image_processor = ImageProcessor()
        self.cache_manager = CacheManager()
        
        # Создание директории для результатов
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def generate_mockups(self, product_image: Image.Image, 
                        logo_image: Image.Image,
                        style: str = "modern",
                        logo_application: str = "embroidery",
                        custom_prompt: str = "",
                        product_color: str = "белый",
                        product_angle: str = "спереди",
                        logo_position: str = "центр",
                        logo_size: str = "средний",
                        logo_color: str = "как на фото",
                        pattern_image: Optional[Image.Image] = None) -> Dict:
        """
        Генерация мокапов с логотипом
        
        Args:
            product_image: Изображение товара
            logo_image: Логотип клиента
            style: Стиль мокапа
            logo_application: Тип нанесения логотипа
            custom_prompt: Дополнительные детали для промпта
            product_color: Цвет товара
            product_angle: Ракурс товара
            logo_position: Расположение логотипа
            logo_size: Размер логотипа
            logo_color: Цвет логотипа
            pattern_image: Паттерн для использования (опционально)
        
        Returns:
            Словарь с результатами генерации
        """
        
        start_time = time.time()
        
        # Генерация хешей для кэширования
        product_hash = self._generate_image_hash(product_image)
        logo_hash = self._generate_image_hash(logo_image)
        
        # Проверка кэша
        cache_key = self.cache_manager.generate_cache_key(
            product_hash, logo_hash, style, {
                "logo_application": logo_application, 
                "custom_prompt": custom_prompt, 
                "product_color": product_color, 
                "product_angle": product_angle,
                "logo_position": logo_position,
                "logo_size": logo_size,
                "logo_color": logo_color
            }
        )
        
        cached_result = self.cache_manager.get_cached_result(cache_key)
        if cached_result:
            print("Использован кэшированный результат")
            return {
                "status": "success",
                "source": "cache",
                "mockups": cached_result["result"]["mockups"],
                "processing_time": time.time() - start_time,
                "cache_key": cache_key
            }
        
        # Обработка изображений
        processed_product = self.image_processor.optimize_for_api(product_image)
        processed_logo = self.image_processor.optimize_for_api(logo_image)
        processed_pattern = self.image_processor.optimize_for_api(pattern_image) if pattern_image else None
        
        # Генерация через Gemini API
        try:
            gemini_results = self.gemini_client.generate_mockup(
                processed_product, processed_logo, style, logo_application, custom_prompt, product_color, product_angle, logo_position, logo_size, logo_color, processed_pattern
            )
            
            # Проверка, есть ли изображения от Gemini
            gemini_has_images = any("image_data" in mockup for mockup in gemini_results)
            
            if not gemini_has_images:
                # Если нет изображений от Gemini - возвращаем ошибку
                return {
                    "status": "error",
                    "source": "gemini_no_images",
                    "mockups": {"gemini_mockups": [], "fallback_used": True},
                    "error": "Gemini не сгенерировал изображения",
                    "processing_time": time.time() - start_time
                }
            
            # Создаем результат только с Gemini мокапами
            all_mockups = {
                "gemini_mockups": gemini_results,
                "fallback_used": False
            }
            
            # Создаем версию для кэша без PIL Image объектов
            cache_data = {
                "gemini_mockups": [
                    {
                        "style": mockup.get("style"),
                        "logo_application": mockup.get("logo_application"),
                        "product_type": mockup.get("product_type"),
                        "source": mockup.get("source"),
                        "text_response": mockup.get("text_response")
                    } for mockup in gemini_results if "image" in mockup
                ],
                "fallback_used": False
            }
            
            # Сохранение в кэш
            self.cache_manager.save_to_cache(cache_key, cache_data)
            
            # Сохранение изображений
            saved_paths = self._save_mockups(all_mockups, cache_key)
            
            # Сохранение в историю проекта
            history_paths = []
            for mockup in gemini_results:
                if "image_data" in mockup:
                    history_path = self._save_mockup_to_history(mockup, style, logo_application, custom_prompt, product_color, product_angle)
                    history_paths.append(history_path)
            
            return {
                "status": "success",
                "source": "generated",
                "mockups": all_mockups,
                "saved_paths": saved_paths,
                "history_paths": history_paths,
                "processing_time": time.time() - start_time,
                "cache_key": cache_key
            }
            
        except Exception as e:
            print(f"Ошибка генерации: {e}")
            
            return {
                "status": "error",
                "source": "generation_failed",
                "mockups": {"gemini_mockups": [], "fallback_used": True},
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def _generate_image_hash(self, image: Image.Image) -> str:
        """Генерация хеша изображения"""
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        image_bytes = buffer.getvalue()
        
        import hashlib
        return hashlib.md5(image_bytes).hexdigest()
    
    def _create_local_mockups(self, product_image: Image.Image, 
                             logo_image: Image.Image,
                             positions: List[str]) -> List[Dict]:
        """Создание локальных мокапов как fallback"""
        mockups = []
        
        for i, position in enumerate(positions):
            try:
                mockup = self.image_processor.create_mockup_template(
                    product_image, logo_image, position
                )
                
                # Сохраняем изображение на диск
                import os
                import time
                timestamp = int(time.time())
                filename = f"local_mockup_{timestamp}_{i+1}.jpg"
                filepath = os.path.join("outputs", filename)
                
                # Создаем папку outputs если не существует
                os.makedirs("outputs", exist_ok=True)
                
                # Сохраняем изображение
                mockup.save(filepath, "JPEG", quality=95)
                
                mockups.append({
                    "id": f"local_{i+1}",
                    "position": position,
                    "image": mockup,
                    "image_path": filepath,
                    "description": f"Локальный мокап с логотипом в позиции {position}",
                    "type": "local"
                })
            except Exception as e:
                print(f"Ошибка создания локального мокапа {position}: {e}")
        
        return mockups
    
    def _save_mockup_to_history(self, mockup_data: dict, style: str, logo_application: str, custom_prompt: str = "", product_color: str = "белый", product_angle: str = "спереди") -> str:
        """Сохранение мокапа в историю проекта"""
        import os
        import time
        from datetime import datetime
        
        # Создаем папку для истории
        history_dir = os.path.join(OUTPUT_DIR, "history")
        os.makedirs(history_dir, exist_ok=True)
        
        # Генерируем имя файла с метаданными
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mockup_{timestamp}_{style}_{logo_application}.jpg"
        if custom_prompt:
            # Ограничиваем длину custom_prompt в имени файла
            prompt_short = custom_prompt[:20].replace(" ", "_").replace("/", "_")
            filename = f"mockup_{timestamp}_{style}_{logo_application}_{prompt_short}.jpg"
        
        filepath = os.path.join(history_dir, filename)
        
        # Сохраняем изображение
        if "image" in mockup_data:
            mockup_data["image"].save(filepath, "JPEG", quality=95)
        elif "image_data" in mockup_data:
            with open(filepath, "wb") as f:
                f.write(mockup_data["image_data"])
        
        # Создаем файл с метаданными
        metadata_file = filepath.replace(".jpg", "_metadata.txt")
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Стиль: {style}\n")
            f.write(f"Цвет товара: {product_color}\n")
            f.write(f"Ракурс товара: {product_angle}\n")
            f.write(f"Тип нанесения: {logo_application}\n")
            f.write(f"Дополнительные требования: {custom_prompt}\n")
            f.write(f"Источник: {mockup_data.get('source', 'unknown')}\n")
            f.write(f"Тип продукта: {mockup_data.get('product_type', 'unknown')}\n")
        
        print(f"✅ Мокап сохранен в историю: {filepath}")
        return filepath
    
    def _save_mockups(self, mockups: Dict, cache_key: str) -> Dict:
        """Сохранение мокапов в файлы"""
        saved_paths = {}
        
        try:
            # Сохранение локальных мокапов
            if "local_mockups" in mockups:
                for mockup in mockups["local_mockups"]:
                    filename = f"{cache_key}_{mockup['id']}.jpg"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    
                    mockup["image"].save(filepath, "JPEG", quality=95)
                    saved_paths[mockup["id"]] = filepath
            
            # Сохранение Gemini мокапов (если есть изображения)
            if "gemini_mockups" in mockups:
                for i, mockup in enumerate(mockups["gemini_mockups"]):
                    if "image_data" in mockup:
                        filename = f"{cache_key}_gemini_{i+1}.jpg"
                        filepath = os.path.join(OUTPUT_DIR, filename)
                        
                        # Декодирование base64 изображения
                        image_data = base64.b64decode(mockup["image_data"])
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        
                        saved_paths[f"gemini_{i+1}"] = filepath
        
        except Exception as e:
            print(f"Ошибка сохранения мокапов: {e}")
        
        return saved_paths
    
    def get_generation_stats(self) -> Dict:
        """Получение статистики генерации"""
        cache_stats = self.cache_manager.get_cache_stats()
        
        return {
            "cache_stats": cache_stats,
            "output_directory": OUTPUT_DIR,
            "batch_size": BATCH_SIZE,
            "timestamp": time.time()
        }
    
    def cleanup_old_outputs(self, days_old: int = 7) -> int:
        """Очистка старых результатов"""
        import time
        import glob
        
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 3600)
        removed_count = 0
        
        try:
            pattern = os.path.join(OUTPUT_DIR, "*.jpg")
            for filepath in glob.glob(pattern):
                if os.path.getctime(filepath) < cutoff_time:
                    os.remove(filepath)
                    removed_count += 1
        except Exception as e:
            print(f"Ошибка очистки старых файлов: {e}")
        
        return removed_count
