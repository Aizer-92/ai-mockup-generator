"""
Клиент для работы с Gemini 2.5 Flash API (Nano Banana)
Использует новый официальный API для генерации изображений
"""
from google import genai
from google.genai import types
import base64
import io
from PIL import Image
import json
import time
from typing import List, Dict, Optional
from config import get_config, GEMINI_MODEL, GEMINI_ANALYSIS_MODEL, MAX_IMAGE_SIZE, COMPRESSION_QUALITY

class GeminiClient:
    def __init__(self):
        """Инициализация клиента Gemini 2.5 Flash"""
        # Получаем актуальную конфигурацию
        config = get_config()
        api_key = config['GEMINI_API_KEY']
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
        
        # Инициализация нового клиента
        self.client = genai.Client(api_key=api_key)
        
    def compress_image(self, image: Image.Image) -> Image.Image:
        """Сжатие изображения для экономии токенов"""
        # Ресайз если нужно
        if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
            image.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
        
        # Конвертация в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def detect_product_type(self, product_image: Image.Image) -> str:
        """Определение типа продукта по изображению"""
        # Простое определение по цветам и текстуре
        colors = product_image.getcolors(maxcolors=256*256*256)
        if colors:
            dominant_color = max(colors, key=lambda x: x[0])
            # Простая эвристика для определения типа продукта
            if dominant_color[1][0] > 200 and dominant_color[1][1] > 200 and dominant_color[1][2] > 200:
                return "textile"  # Светлые цвета - текстиль
            elif dominant_color[1][0] < 100 and dominant_color[1][1] < 100 and dominant_color[1][2] < 100:
                return "leather"  # Темные цвета - кожа
            else:
                return "fabric"   # Остальное - ткань
        return "fabric"
    
    def generate_mockup(self, product_image: Image.Image, logo_image: Image.Image, 
                       mockup_style: str = "modern", logo_application: str = "embroidery", 
                       custom_prompt: str = "", product_color: str = "белый", 
                       product_angle: str = "спереди", logo_position: str = "центр",
                       logo_size: str = "средний", logo_color: str = "как на фото",
                       pattern_image: Optional[Image.Image] = None) -> List[Dict]:
        """
        Генерация мокапа с логотипом используя Gemini 2.5 Flash
        
        Args:
            product_image: Изображение товара
            logo_image: Логотип клиента
            mockup_style: Стиль мокапа (modern, vintage, minimal, luxury)
            logo_application: Тип нанесения логотипа
            custom_prompt: Дополнительные требования к промпту
            product_color: Цвет товара
            product_angle: Ракурс товара
            logo_position: Расположение логотипа
            logo_size: Размер логотипа
            logo_color: Цвет логотипа
            pattern_image: Паттерн для использования (опционально)
        
        Returns:
            Список сгенерированных мокапов
        """
        
        # Подготовка изображений
        processed_product = self.compress_image(product_image)
        processed_logo = self.compress_image(logo_image)
        processed_pattern = self.compress_image(pattern_image) if pattern_image else None
        
        # Определение типа продукта
        product_type = self.detect_product_type(processed_product)
        
        # Универсальный промпт для разных материалов и носителей
        material_adaptations = {
            "fabric": {
                "embroidery": "embroidered with raised thread texture, realistic stitching details, and natural fabric integration",
                "printing": "printed with smooth, flat surface, crisp edges, and fabric-appropriate ink absorption",
                "woven": "woven into the fabric with integrated texture, natural appearance, and seamless blending",
                "embossed": "embossed with raised relief effect, realistic depth, and fabric-appropriate texture",
                "sublimation": "sublimated with vibrant colors, smooth finish, and permanent integration into fabric",
                "silicone": "silicone application with soft, flexible texture, raised surface, and durable finish",
                "patch": "patch application with raised edges, fabric backing, and sewn-on appearance",
                "heat_transfer": "heat transfer with smooth application, vibrant colors, and professional finish",
                "screen_print": "screen printed with thick ink, matte finish, and durable application",
                "digital_print": "digitally printed with high resolution, smooth finish, and precise details",
                "laser_engraving": "laser engraved with subtle texture, permanent marking, and professional appearance"
            },
            "textile": {
                "embroidery": "embroidered with raised thread texture, realistic stitching details, and textile-appropriate integration",
                "printing": "printed with smooth, flat surface, crisp edges, and textile-appropriate ink absorption",
                "woven": "woven into the textile with integrated texture, natural appearance, and seamless blending",
                "embossed": "embossed with raised relief effect, realistic depth, and textile-appropriate texture",
                "sublimation": "sublimated with vibrant colors, smooth finish, and permanent integration into textile",
                "silicone": "silicone application with soft, flexible texture, raised surface, and durable finish",
                "patch": "patch application with raised edges, fabric backing, and sewn-on appearance",
                "heat_transfer": "heat transfer with smooth application, vibrant colors, and professional finish",
                "screen_print": "screen printed with thick ink, matte finish, and durable application",
                "digital_print": "digitally printed with high resolution, smooth finish, and precise details",
                "laser_engraving": "laser engraved with subtle texture, permanent marking, and professional appearance"
            },
            "leather": {
                "embroidery": "embroidered with raised thread texture, realistic stitching details, and leather-appropriate integration",
                "printing": "printed with smooth, flat surface, crisp edges, and leather-appropriate ink absorption",
                "woven": "woven into the leather with integrated texture, natural appearance, and seamless blending",
                "embossed": "embossed with raised relief effect, realistic depth, and leather-appropriate texture",
                "sublimation": "sublimated with vibrant colors, smooth finish, and permanent integration into leather",
                "silicone": "silicone application with soft, flexible texture, raised surface, and durable finish",
                "patch": "patch application with raised edges, fabric backing, and sewn-on appearance",
                "heat_transfer": "heat transfer with smooth application, vibrant colors, and professional finish",
                "screen_print": "screen printed with thick ink, matte finish, and durable application",
                "digital_print": "digitally printed with high resolution, smooth finish, and precise details",
                "laser_engraving": "laser engraved with subtle texture, permanent marking, and professional appearance"
            }
        }
        
        style_descriptions = {
            "modern": "Modern clean lines, minimalist design, contemporary colors, sleek presentation with bright, clean lighting and sharp contrasts",
            "luxury": "Premium materials, elegant presentation, sophisticated look, high-end appeal with dramatic lighting and rich textures",
            "minimal": "Simple design, neutral colors, clean aesthetics, uncluttered presentation with soft, even lighting and subtle shadows",
            "dynamic": "Energetic, vibrant design with bold colors, dynamic composition, action-oriented presentation with dramatic lighting and movement"
        }
        
        # Получаем эффект для логотипа с детальной отладкой
        material_dict = material_adaptations.get(product_type, material_adaptations["fabric"])
        print(f"Material dict for '{product_type}': {list(material_dict.keys())}")
        print(f"Looking for logo_application: '{logo_application}'")
        
        if logo_application in material_dict:
            logo_effect = material_dict[logo_application]
            print(f"✅ Found logo_effect: '{logo_effect}'")
        else:
            # Если не найден, используем первый доступный (не embroidery)
            available_methods = [k for k in material_dict.keys() if k != "embroidery"]
            if available_methods:
                fallback_method = available_methods[0]
                logo_effect = material_dict[fallback_method]
                print(f"⚠️ Logo application '{logo_application}' not found, using fallback: '{fallback_method}' -> '{logo_effect}'")
            else:
                logo_effect = material_dict["embroidery"]
                print(f"⚠️ Only embroidery available, using: '{logo_effect}'")
        
        # Двухэтапный промпт: сначала товар, потом логотип
        # Обработка опций "как на фото"
        color_instruction = "keep the original color from the product image" if product_color == "как на фото" else f"make the product {product_color}"
        angle_instruction = "keep the original angle from the product image" if product_angle == "как на фото" else f"photograph from {product_angle} angle"
        logo_color_instruction = "keep the original color from the logo image" if logo_color == "как на фото" else f"make the logo {logo_color}"
        
        # Словари для перевода
        position_translation = {
            "центр": "center of the product",
            "верхний левый угол": "top-left corner of the product",
            "верхний правый угол": "top-right corner of the product", 
            "нижний левый угол": "bottom-left corner of the product",
            "нижний правый угол": "bottom-right corner of the product",
            "левый бок": "left side of the product",
            "правый бок": "right side of the product",
            "верх": "top of the product",
            "низ": "bottom of the product"
        }
        
        size_translation = {
            "очень маленький": "very small",
            "маленький": "small",
            "средний": "medium",
            "большой": "large",
            "очень большой": "very large"
        }
        
        position_english = position_translation.get(logo_position, "center")
        size_english = size_translation.get(logo_size, "medium")
        
        prompt = f"""🚨 CRITICAL INSTRUCTION: DO NOT CHANGE THE PRODUCT TYPE! 🚨

You must keep the EXACT SAME PRODUCT from the uploaded image. If it's a phone stand, keep it as a phone stand. If it's a car seat cover, keep it as a car seat cover. If it's a car organizer, keep it as a car organizer.

TASK: Add logo to the existing product WITHOUT changing what the product is.

PRODUCT PRESERVATION (MOST IMPORTANT):
- Keep the EXACT product type from the uploaded image
- Keep the same design, shape, and features
- Only change: color (if specified), angle (if specified), and add logo
- DO NOT transform the product into something else
- REMOVE ALL EXISTING BRANDING, LOGOS, TEXT from the original product
- Make the product clean and unbranded before adding the new logo

STYLE AND APPEARANCE:
- Style: {mockup_style} style with {style_descriptions.get(mockup_style, style_descriptions['modern'])}
- Color: {color_instruction}
- Photography: {angle_instruction}

LOGO APPLICATION:
Apply logo using {logo_application} method: {logo_effect}
Logo position: {position_english}
Logo size: {size_english}
Logo color: {logo_color_instruction}
Logo must follow product curves and texture naturally.

{f"SPECIAL REQUIREMENTS: {custom_prompt}" if custom_prompt.strip() else ""}

{f"PATTERN APPLICATION: Use the uploaded pattern image to create a repeating pattern across the product surface. The pattern should be seamlessly integrated with the product design." if processed_pattern else ""}

FINAL REQUIREMENTS:
- Keep the original product exactly as shown in the image
- Only add the logo to the existing product
- Professional studio lighting
- Clean background
- High quality image

Generate the mockup image."""
        
        # Отладочная информация
        print(f"Mockup style: '{mockup_style}'")
        print(f"Product color: '{product_color}'")
        print(f"Product angle: '{product_angle}'")
        print(f"Logo application: '{logo_application}'")
        print(f"Logo position: '{logo_position}' -> '{position_english}'")
        print(f"Logo size: '{logo_size}' -> '{size_english}'")
        print(f"Logo color: '{logo_color}'")
        print(f"Product type: '{product_type}'")
        print(f"Logo effect: '{logo_effect}'")
        print(f"Custom prompt: '{custom_prompt}'")
        print(f"Custom prompt length: {len(custom_prompt.strip()) if custom_prompt else 0}")
        if custom_prompt.strip():
            print(f"Final prompt includes custom requirements: {custom_prompt}")
        
        # Выводим полный промпт для отладки
        print("=" * 50)
        print("ПОЛНЫЙ ПРОМПТ ДЛЯ GEMINI:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        
        try:
            # Используем новый API Gemini 2.5 Flash
            contents = [prompt, processed_product, processed_logo]
            if processed_pattern:
                contents.append(processed_pattern)
            
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
            )
            
            # Обработка ответа
            mockups = []
            has_images = False
            text_response = ""
            
            # Выводим полный ответ для отладки
            print("=" * 50)
            print("ПОЛНЫЙ ОТВЕТ ОТ GEMINI:")
            print("=" * 50)
            print(f"Количество кандидатов: {len(response.candidates)}")
            if response.candidates:
                print(f"Количество частей в ответе: {len(response.candidates[0].content.parts)}")
                for i, part in enumerate(response.candidates[0].content.parts):
                    print(f"Часть {i+1}:")
                    if part.text is not None:
                        print(f"Текст: {part.text}")
                    elif part.inline_data is not None:
                        print(f"Изображение: {len(part.inline_data.data)} байт")
                    else:
                        print(f"Неизвестный тип: {type(part)}")
            print("=" * 50)
            
            # Сначала собираем все части ответа
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response += part.text + " "
                    print(f"Текстовый ответ от Gemini: {part.text}")
                elif part.inline_data is not None:
                    has_images = True
                    # Декодируем изображение
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    
                    mockup = {
                        "image": image,
                        "image_data": image_data,
                        "style": mockup_style,
                        "logo_application": logo_application,
                        "product_type": product_type,
                        "source": "gemini_2.5_flash",
                        "text_response": text_response.strip() if text_response else None
                    }
                    mockups.append(mockup)
            
            # Если есть изображения - возвращаем их (даже если есть текст)
            if mockups:
                print(f"✅ Получено {len(mockups)} изображений от Gemini")
                return mockups
            
            # Если нет изображений - fallback
            return [{"fallback_needed": True, "text": text_response or "No images generated by Gemini"}]
            
        except Exception as e:
            print(f"Ошибка генерации через Gemini 2.5 Flash: {e}")
            return [{"fallback_needed": True, "error": str(e)}]
    
    def generate_with_files(self, prompt: str, files: List[Dict]) -> str:
        """
        Генерация текста с файлами (для анализа брендбука)
        
        Args:
            prompt: Текстовый промпт
            files: Список файлов с ключами 'data', 'mime_type', 'name'
            
        Returns:
            str: Ответ от Gemini
        """
        try:
            # Подготавливаем содержимое
            contents = [prompt]
            
            # Добавляем файлы
            for file_info in files:
                if file_info['mime_type'].startswith('image/'):
                    # Для изображений
                    if hasattr(file_info['data'], 'read'):
                        # Если это файловый объект
                        image_data = file_info['data'].read()
                    else:
                        # Если это bytes
                        image_data = file_info['data']
                    
                    # Конвертируем в base64
                    image_b64 = base64.b64encode(image_data).decode('utf-8')
                    contents.append({
                        "inline_data": {
                            "mime_type": file_info['mime_type'],
                            "data": image_b64
                        }
                    })
                elif file_info['mime_type'] == 'application/pdf':
                    # Для PDF файлов
                    if hasattr(file_info['data'], 'read'):
                        pdf_data = file_info['data'].read()
                    else:
                        pdf_data = file_info['data']
                    
                    pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
                    contents.append({
                        "inline_data": {
                            "mime_type": file_info['mime_type'],
                            "data": pdf_b64
                        }
                    })
            
            # Отправляем запрос
            response = self.client.models.generate_content(
                model=GEMINI_ANALYSIS_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048
                )
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Ошибка генерации с файлами: {e}")
            return ""

    def generate_mockup_with_analysis(self, product_image: Image.Image, logo_image: Image.Image, 
                                    analysis_recommendations: Dict, custom_prompt: str = "", 
                                    pattern_image: Optional[Image.Image] = None) -> List[Dict]:
        """
        Генерация мокапа с рекомендациями из анализа коллекции
        
        Args:
            product_image: Изображение товара
            logo_image: Логотип клиента
            analysis_recommendations: Рекомендации из анализа (style, logo_application, logo_position, etc.)
            custom_prompt: Дополнительные требования
            pattern_image: Паттерн для использования (опционально)
        
        Returns:
            Список с результатами генерации
        """
        
        # Извлекаем рекомендации из анализа
        mockup_style = analysis_recommendations.get("style", "modern")
        logo_application = analysis_recommendations.get("logo_application", "embroidery")
        logo_position = analysis_recommendations.get("logo_position", "центр")
        logo_size = analysis_recommendations.get("logo_size", "средний")
        logo_color = analysis_recommendations.get("logo_color", "как на фото")
        product_color = analysis_recommendations.get("product_color", "как на фото")
        product_angle = analysis_recommendations.get("product_angle", "как на фото")
        
        # Объединяем custom_prompt с рекомендациями
        analysis_custom = analysis_recommendations.get("custom_prompt", "")
        combined_custom = f"{analysis_custom} {custom_prompt}".strip()
        
        # Используем основной метод генерации с рекомендациями
        return self.generate_mockup(
            product_image, logo_image, mockup_style, logo_application, 
            combined_custom, product_color, product_angle, logo_position, 
            logo_size, logo_color, pattern_image
        )
    
    def _parse_response(self, response) -> List[Dict]:
        """Парсинг ответа от Gemini API"""
        mockups = []
        
        try:
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(f"Текстовый ответ: {part.text}")
                    return [{"fallback_needed": True, "text": part.text}]
                elif part.inline_data is not None:
                    # Декодируем изображение
                    image_data = part.inline_data.data
                    image = Image.open(io.BytesIO(image_data))
                    
                    mockup = {
                        "image": image,
                        "image_data": image_data,
                        "source": "gemini_2.5_flash"
                    }
                    mockups.append(mockup)
            
            return mockups if mockups else [{"fallback_needed": True, "text": "No images generated"}]
            
        except Exception as e:
            print(f"Ошибка парсинга ответа: {e}")
            return [{"fallback_needed": True, "error": str(e)}]
    
    def analyze_collection(self, product_images: List[Image.Image], 
                          logo_image: Image.Image, 
                          collection_prompt: str) -> Optional[Dict]:
        """
        Анализ коллекции товаров и создание индивидуальных промптов
        
        Args:
            product_images: Список изображений товаров
            logo_image: Логотип клиента
            collection_prompt: Промпт для анализа коллекции
        
        Returns:
            Словарь с индивидуальными промптами или None при ошибке
        """
        
        try:
            # Подготовка изображений
            compressed_products = [self.compress_image(img) for img in product_images]
            compressed_logo = self.compress_image(logo_image)
            
            # Создание контента для запроса согласно новой документации
            parts = []
            
            # Добавляем промпт как текст
            parts.append(collection_prompt)
            
            # Добавляем логотип с указанием типа
            logo_buffer = io.BytesIO()
            
            # Убеждаемся, что логотип в RGB режиме для JPEG
            if compressed_logo.mode == 'RGBA':
                # Создаем белый фон для RGBA изображений
                background = Image.new('RGB', compressed_logo.size, (255, 255, 255))
                background.paste(compressed_logo, mask=compressed_logo.split()[-1])
                compressed_logo = background
            elif compressed_logo.mode != 'RGB':
                compressed_logo = compressed_logo.convert('RGB')
            
            compressed_logo.save(logo_buffer, format='JPEG', quality=COMPRESSION_QUALITY)
            logo_data = logo_buffer.getvalue()
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(logo_data).decode()
                }
            })
            
            # Добавляем изображения товаров с указанием типа
            for i, product_img in enumerate(compressed_products):
                product_buffer = io.BytesIO()
                
                # Убеждаемся, что изображение товара в RGB режиме для JPEG
                if product_img.mode == 'RGBA':
                    # Создаем белый фон для RGBA изображений
                    background = Image.new('RGB', product_img.size, (255, 255, 255))
                    background.paste(product_img, mask=product_img.split()[-1])
                    product_img = background
                elif product_img.mode != 'RGB':
                    product_img = product_img.convert('RGB')
                
                product_img.save(product_buffer, format='JPEG', quality=COMPRESSION_QUALITY)
                product_data = product_buffer.getvalue()
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(product_data).decode()
                    }
                })
            
            # Отправка запроса согласно новой документации
            print(f"Отправляем запрос на анализ коллекции...")
            print(f"Количество частей контента: {len(parts)}")
            print(f"1. Текст промпта: {len(collection_prompt)} символов")
            print(f"2. Логотип: {len(logo_data)} байт")
            print(f"3-{len(parts)}. Товары: {len(compressed_products)} изображений")
            
            response = self.client.models.generate_content(
                model=GEMINI_ANALYSIS_MODEL,
                contents=parts,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            if response and response.text:
                print(f"Получен ответ от Gemini: {response.text[:200]}...")
                
                # Парсинг JSON ответа
                try:
                    # Извлекаем JSON из ответа
                    response_text = response.text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    result = json.loads(response_text)
                    print(f"Успешно распарсен JSON с {len(result.get('individual_prompts', []))} промптами")
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"Ошибка парсинга JSON: {e}")
                    print(f"Ответ от Gemini: {response.text}")
                    return None
            else:
                print("Нет текстового ответа от Gemini")
                return None
            
        except Exception as e:
            print(f"Ошибка анализа коллекции: {e}")
            return None
    
    def analyze_collection_text_only(self, num_products: int, collection_prompt: str) -> Optional[Dict]:
        """
        Альтернативный анализ коллекции только по тексту (без изображений)
        
        Args:
            num_products: Количество товаров
            collection_prompt: Промпт для анализа коллекции
        
        Returns:
            Словарь с индивидуальными промптами или None при ошибке
        """
        
        try:
            # Отправка запроса только с текстом согласно новой документации
            print("Отправляем текстовый запрос на анализ коллекции...")
            response = self.client.models.generate_content(
                model=GEMINI_ANALYSIS_MODEL,
                contents=collection_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )
            )
            
            if response and response.text:
                print(f"Получен текстовый ответ от Gemini: {response.text[:200]}...")
                
                # Парсинг JSON ответа
                try:
                    # Извлекаем JSON из ответа
                    response_text = response.text.strip()
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    result = json.loads(response_text)
                    print(f"Успешно распарсен JSON с {len(result.get('individual_prompts', []))} промптами")
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"Ошибка парсинга JSON: {e}")
                    print(f"Ответ от Gemini: {response.text}")
                    return None
            else:
                print("Нет текстового ответа от Gemini")
                return None
            
        except Exception as e:
            print(f"Ошибка текстового анализа коллекции: {e}")
            return None