"""
Модуль для пакетной обработки изображений
Создает коллекции товаров в едином стиле
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

class BatchProcessor:
    def __init__(self):
        """Инициализация пакетного процессора"""
        self.gemini_client = GeminiClient()
        self.image_processor = ImageProcessor()
        self.cache_manager = CacheManager()
        
        # Создание директории для результатов
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, "batch"), exist_ok=True)
    
    def analyze_collection(self, product_images: List[Image.Image], 
                          logo_image: Image.Image,
                          product_color: str = "как на фото",
                          collection_style: str = "modern",
                          collection_theme: str = "",
                          product_names: List[str] = None) -> Dict:
        """
        Анализ коллекции и создание индивидуальных промптов для каждого товара
        
        Args:
            product_images: Список изображений товаров
            logo_image: Логотип клиента
            product_color: Цвет товаров
            collection_style: Стиль коллекции
            collection_theme: Тема коллекции
            product_names: Список названий товаров
        
        Returns:
            Словарь с индивидуальными промптами для каждого товара
        """
        
        start_time = time.time()
        
        try:
            # Обработка изображений для API
            processed_products = []
            for img in product_images:
                processed_img = self.image_processor.optimize_for_api(img)
                processed_products.append(processed_img)
            
            processed_logo = self.image_processor.optimize_for_api(logo_image)
            
            # Создание промпта для анализа коллекции
            collection_prompt = self._create_collection_analysis_prompt(
                product_color, collection_style, collection_theme, len(product_images), product_names
            )
            
            # Отправка запроса в Gemini для анализа коллекции
            print(f"Анализируем коллекцию из {len(processed_products)} товаров...")
            analysis_result = self.gemini_client.analyze_collection(
                processed_products, processed_logo, collection_prompt
            )
            
            if analysis_result and "individual_prompts" in analysis_result:
                print(f"✅ AI анализ успешен, получено {len(analysis_result['individual_prompts'])} промптов")
                return {
                    "status": "success",
                    "individual_prompts": analysis_result["individual_prompts"],
                    "collection_theme": analysis_result.get("collection_theme", collection_theme),
                    "processing_time": time.time() - start_time
                }
            else:
                print("⚠️ AI анализ с изображениями не удался, пробуем текстовый анализ...")
                # Пробуем альтернативный текстовый анализ
                text_analysis_result = self.gemini_client.analyze_collection_text_only(
                    len(product_images), collection_prompt
                )
                
                if text_analysis_result and "individual_prompts" in text_analysis_result:
                    print(f"✅ Текстовый AI анализ успешен, получено {len(text_analysis_result['individual_prompts'])} промптов")
                    return {
                        "status": "success",
                        "individual_prompts": text_analysis_result["individual_prompts"],
                        "collection_theme": text_analysis_result.get("collection_theme", collection_theme),
                        "processing_time": time.time() - start_time
                    }
                else:
                    print("⚠️ Текстовый AI анализ тоже не удался, используем fallback промпты")
                # Fallback - создаем базовые промпты
                return self._create_fallback_prompts(
                    product_images, product_color, collection_style, collection_theme, product_names
                )
                
        except Exception as e:
            print(f"Ошибка анализа коллекции: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def process_batch(self, product_images: List[Image.Image], 
                     logo_image: Image.Image, 
                     individual_prompts: List[Dict],
                     collection_settings: Dict,
                     product_names: List[str] = None) -> Dict:
        """
        Пакетная обработка изображений с индивидуальными промптами
        
        Args:
            product_images: Список изображений товаров
            logo_image: Логотип клиента
            individual_prompts: Список индивидуальных промптов
            collection_settings: Настройки коллекции
            product_names: Список названий товаров
        
        Returns:
            Словарь с результатами обработки
        """
        
        start_time = time.time()
        results = []
        
        try:
            # Инициализируем названия товаров если не переданы
            if product_names is None:
                product_names = [f"Товар {i+1}" for i in range(len(product_images))]
            
            for i, (product_img, prompt_data, product_name) in enumerate(zip(product_images, individual_prompts, product_names)):
                print(f"Обработка товара {i+1}/{len(product_images)}: {product_name}")
                
                # Используем ОРИГИНАЛЬНОЕ изображение товара (не обработанное)
                # Обрабатываем только для API (сжатие), но не меняем сам товар
                processed_product = self.image_processor.optimize_for_api(product_img)
                processed_logo = self.image_processor.optimize_for_api(logo_image)
                
                # Генерация мокапа с рекомендациями из анализа (используем промпт из одиночной генерации)
                mockup_result = self.gemini_client.generate_mockup_with_analysis(
                    processed_product, processed_logo, prompt_data, ""
                )
                
                if mockup_result and len(mockup_result) > 0:
                    mockup = mockup_result[0]
                    results.append({
                        "index": i,
                        "product_name": product_name,
                        "original_image": product_img,
                        "mockup": mockup,
                        "prompt_data": prompt_data,
                        "status": "success"
                    })
                else:
                    results.append({
                        "index": i,
                        "product_name": product_name,
                        "original_image": product_img,
                        "mockup": None,
                        "prompt_data": prompt_data,
                        "status": "failed",
                        "error": "Не удалось сгенерировать мокап"
                    })
                
                # Небольшая пауза между запросами
                time.sleep(1)
            
            # Сохранение результатов
            saved_paths = self._save_batch_results(results, collection_settings)
            
            return {
                "status": "success",
                "results": results,
                "saved_paths": saved_paths,
                "total_processed": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"Ошибка пакетной обработки: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": results,
                "processing_time": time.time() - start_time
            }
    
    def _create_collection_analysis_prompt(self, product_color: str, collection_style: str, 
                                         collection_theme: str, num_products: int, product_names: List[str] = None) -> str:
        """Создание промпта для анализа коллекции"""
        
        # Добавляем названия товаров в промпт
        products_info = ""
        if product_names:
            products_info = "\nТОВАРЫ В КОЛЛЕКЦИИ:\n"
            for i, name in enumerate(product_names):
                products_info += f"- Товар {i+1}: {name}\n"
        
        # Словарь перевода стилей
        style_translation = {
            "Современный": "modern",
            "Премиальный": "luxury", 
            "Минималистичный": "minimal",
            "В динамике": "dynamic"
        }
        
        collection_style_key = style_translation.get(collection_style, "modern")
        
        return f"""🚨 КРИТИЧЕСКИ ВАЖНО: Анализируй ТОЛЬКО ОСНОВНОЙ ТОВАР на каждом изображении! 🚨

Проанализируй коллекцию из {num_products} товаров и создай индивидуальные промпты для каждого.

НАСТРОЙКИ КОЛЛЕКЦИИ:
- Цвет товаров: {product_color}
- Стиль коллекции: {collection_style} ({collection_style_key})
- Тема коллекции: {collection_theme if collection_theme else "не указана"}
{products_info}

ЗАДАЧА:
1. ВНИМАТЕЛЬНО изучи каждое изображение - определи ОСНОВНОЙ ТОВАР (игнорируй фоновые объекты, людей, окружение)
2. ФОКУСИРУЙСЯ ТОЛЬКО НА ТОВАРЕ: не описывай фон, людей, другие объекты на изображении
3. Для каждого основного товара выбери ПРОСТОЕ И РЕГУЛЯРНОЕ нанесение логотипа:
   - ТОЛЬКО простые методы: печать, вышивка, сублимация
   - НЕ используй сложные методы: тиснение, гравировка, аппликация, винил
   - Выбирай самое простое и надежное нанесение для каждого товара
4. Определи оптимальное размещение логотипа для КАЖДОГО КОНКРЕТНОГО товара
5. Выбери подходящий размер логотипа
6. Определи лучший ракурс для каждого товара
7. Создай индивидуальный промпт для каждого товара
8. Убедись, что все товары выглядят как единая коллекция

КРИТИЧЕСКИЕ ТРЕБОВАНИЯ:
- АНАЛИЗИРУЙ ТОЛЬКО ОСНОВНОЙ ТОВАР: игнорируй фон, людей, окружение, другие объекты
- НЕ МЕНЯЙ ТИП ТОВАРА! Если на фото подставка для телефона - оставь подставку для телефона
- Если на фото чехол на сиденье - оставь чехол на сиденье
- Если на фото органайзер для автомобиля - оставь органайзер для автомобиля
- НЕ ОПИСЫВАЙ ФОНОВЫЕ ОБЪЕКТЫ: не упоминай людей, мебель, окружение в промптах
- Все товары должны иметь одинаковый стиль: {collection_style}
- Логотип должен быть размещен логично для каждого типа товара
- Приоритет: реалистичность нанесения, затем похожесть на остальные товары
- Каждый товар должен иметь уникальные особенности размещения
- Учитывай специфику каждого товара при выборе нанесения
- НЕ добавляй текст "Товар X коллекция" в промпты
- В custom_prompt укажи ТОЛЬКО конкретный тип товара из изображения (без описания фона)

Верни результат в формате JSON с массивом individual_prompts, где каждый элемент содержит:
- style: стиль для товара (всегда {collection_style})
- logo_application: тип нанесения (ТОЛЬКО: embroidery/printing/sublimation - простые методы)
- logo_position: расположение логотипа (центр/верхний левый угол/верхний правый угол/нижний левый угол/нижний правый угол/левый бок/правый бок/верх/низ)
- logo_size: размер логотипа (очень маленький/маленький/средний/большой/очень большой)
- logo_color: цвет логотипа (как на фото - НЕ МЕНЯЙ)
- product_color: цвет товара (используй указанный: {product_color})
- product_angle: ракурс (как на фото/спереди/в полуоборот/сверху/в интерьере/сбоку/под углом)
- custom_prompt: дополнительные детали с указанием ТОЛЬКО конкретного типа товара (БЕЗ описания фона, людей, окружения)
- reasoning: объяснение выбора для этого товара с указанием типа товара (БЕЗ описания фоновых объектов)"""
    
    def _create_fallback_prompts(self, product_images: List[Image.Image], 
                               product_color: str, collection_style: str, 
                               collection_theme: str, product_names: List[str] = None) -> Dict:
        """Создание базовых промптов как fallback"""
        
        applications = ["embroidery", "printing", "sublimation"]  # Только простые методы
        positions = ["центр", "верхний левый угол", "верхний правый угол", "нижний левый угол", "нижний правый угол"]
        sizes = ["маленький", "средний", "большой"]
        angles = ["как на фото", "спереди", "в полуоборот", "сверху", "сбоку"]
        
        # Словарь перевода стилей для fallback
        style_translation = {
            "Современный": "modern",
            "Премиальный": "luxury", 
            "Минималистичный": "minimal",
            "В динамике": "dynamic"
        }
        
        collection_style_key = style_translation.get(collection_style, "modern")
        
        individual_prompts = []
        for i, img in enumerate(product_images):
            product_name = product_names[i] if product_names and i < len(product_names) else f"Товар {i+1}"
            prompt_data = {
                "style": collection_style_key,  # Единый стиль для всех
                "logo_application": applications[i % len(applications)],
                "logo_position": positions[i % len(positions)],
                "logo_size": sizes[i % len(sizes)],
                "logo_color": "как на фото",  # Логотип не меняем
                "product_color": product_color,
                "product_angle": angles[i % len(angles)],
                "custom_prompt": f"Сохранить оригинальный тип товара '{product_name}' из изображения",  # Указываем сохранить тип товара
                "reasoning": f"Базовый промпт для {product_name} с реалистичным нанесением. Сохранить оригинальный тип товара."
            }
            individual_prompts.append(prompt_data)
        
        return {
            "status": "fallback",
            "individual_prompts": individual_prompts,
            "collection_theme": collection_theme,
            "processing_time": 0
        }
    
    def _save_batch_results(self, results: List[Dict], collection_settings: Dict) -> List[str]:
        """Сохранение результатов пакетной обработки"""
        
        saved_paths = []
        timestamp = int(time.time())
        collection_name = collection_settings.get("collection_theme", f"collection_{timestamp}")
        
        try:
            for result in results:
                if result["status"] == "success" and result["mockup"]:
                    # Создаем имя файла с названием товара
                    product_name = result.get("product_name", f"item_{result['index']+1}")
                    # Очищаем название от недопустимых символов для имени файла
                    safe_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_name = safe_name.replace(' ', '_')
                    filename = f"batch_{timestamp}_{collection_name}_{safe_name}.jpg"
                    filepath = os.path.join(OUTPUT_DIR, "batch", filename)
                    
                    # Сохраняем изображение
                    if "image_data" in result["mockup"]:
                        with open(filepath, "wb") as f:
                            f.write(result["mockup"]["image_data"])
                    elif "image" in result["mockup"]:
                        result["mockup"]["image"].save(filepath, "JPEG", quality=95)
                    
                    saved_paths.append(filepath)
                    
                    # Сохраняем метаданные
                    metadata_file = filepath.replace(".jpg", "_metadata.txt")
                    with open(metadata_file, "w", encoding="utf-8") as f:
                        f.write(f"Коллекция: {collection_name}\n")
                        f.write(f"Товар: {result['index']+1}\n")
                        f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Промпт: {result['prompt_data']}\n")
        
        except Exception as e:
            print(f"Ошибка сохранения результатов: {e}")
        
        return saved_paths
