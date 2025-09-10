"""
Модуль обработки изображений для мокап-генератора
Оптимизирован для экономичной работы с API
"""
import os
import hashlib
import io
from PIL import Image, ImageOps, ImageFilter, ImageDraw
import cv2
import numpy as np
from typing import Tuple, Optional, List
from config import MAX_IMAGE_SIZE, LOGO_MAX_SIZE, UPLOAD_DIR

class ImageProcessor:
    def __init__(self):
        """Инициализация процессора изображений"""
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    def convert_to_rgb(self, image: Image.Image, background_color: tuple = (255, 255, 255)) -> Image.Image:
        """
        Конвертирует изображение в RGB режим для сохранения в JPEG
        
        Args:
            image: Исходное изображение
            background_color: Цвет фона для RGBA изображений (по умолчанию белый)
            
        Returns:
            Image.Image: Изображение в RGB режиме
        """
        if image.mode == 'RGBA':
            # Создаем фон указанного цвета
            background = Image.new('RGB', image.size, background_color)
            background.paste(image, mask=image.split()[-1])  # Используем альфа-канал как маску
            return background
        elif image.mode == 'LA':
            # Конвертируем LA (Luminance + Alpha) в RGB
            background = Image.new('RGB', image.size, background_color)
            background.paste(image, mask=image.split()[-1])
            return background
        elif image.mode == 'P':
            # Конвертируем палитровое изображение
            return image.convert('RGB')
        elif image.mode != 'RGB':
            # Конвертируем любые другие режимы
            return image.convert('RGB')
        else:
            # Уже в RGB режиме
            return image
    
    def validate_image(self, image_path: str) -> bool:
        """Валидация изображения"""
        try:
            with Image.open(image_path) as img:
                # Проверка формата
                if img.format not in ['JPEG', 'PNG', 'WEBP']:
                    return False
                
                # Проверка размера (не слишком маленькое)
                if img.size[0] < 100 or img.size[1] < 100:
                    return False
                
                return True
        except Exception:
            return False
    
    def optimize_for_api(self, image: Image.Image, target_size: Tuple[int, int] = MAX_IMAGE_SIZE) -> Image.Image:
        """Оптимизация изображения для отправки в API"""
        # Конвертация в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Ресайз с сохранением пропорций
        image.thumbnail(target_size, Image.LANCZOS)
        
        # Улучшение качества
        image = ImageOps.autocontrast(image, cutoff=1)
        
        return image
    
    def extract_logo_region(self, image: Image.Image) -> Optional[Image.Image]:
        """Автоматическое извлечение логотипа из изображения"""
        try:
            # Конвертация в OpenCV формат
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Поиск контуров
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Поиск наибольшего контура (предполагаем, что это логотип)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Извлечение области логотипа
            logo_region = image.crop((x, y, x + w, y + h))
            
            # Оптимизация размера логотипа
            logo_region.thumbnail(LOGO_MAX_SIZE, Image.LANCZOS)
            
            return logo_region
            
        except Exception as e:
            print(f"Ошибка извлечения логотипа: {e}")
            return None
    
    def create_transparent_logo(self, logo_image: Image.Image) -> Image.Image:
        """Создание прозрачного логотипа"""
        if logo_image.mode != 'RGBA':
            logo_image = logo_image.convert('RGBA')
        
        # Удаление белого фона (простой метод)
        data = np.array(logo_image)
        white_pixels = np.all(data[:, :, :3] > [240, 240, 240], axis=2)
        data[white_pixels] = [0, 0, 0, 0]  # Прозрачный
        
        return Image.fromarray(data, 'RGBA')
    
    def generate_image_hash(self, image: Image.Image) -> str:
        """Генерация хеша изображения для кэширования"""
        # Конвертация в байты для хеширования
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        image_bytes = buffer.getvalue()
        
        return hashlib.md5(image_bytes).hexdigest()
    
    def batch_process_images(self, images: List[Image.Image]) -> List[Image.Image]:
        """Батчевая обработка изображений"""
        processed = []
        for img in images:
            processed.append(self.optimize_for_api(img))
        return processed
    
    def create_mockup_template(self, product_image: Image.Image, 
                              logo_image: Image.Image, 
                              position: str = "center") -> Image.Image:
        """Создание улучшенного шаблона мокапа с эффектами (двухэтапный процесс)"""
        
        # ЭТАП 1: Создание базового мокапа товара
        mockup = self.create_base_mockup(product_image)
        
        # ЭТАП 2: Интеграция логотипа
        mockup = self.integrate_logo(mockup, logo_image, position)
        
        return mockup
    
    def create_base_mockup(self, product_image: Image.Image) -> Image.Image:
        """Создание базового мокапа товара с улучшениями"""
        # Создание копии изображения товара
        mockup = product_image.copy()
        
        # Конвертация в RGB если нужно (исправление RGBA ошибки)
        if mockup.mode == 'RGBA':
            # Создаем белый фон для RGBA изображений
            background = Image.new('RGB', mockup.size, (255, 255, 255))
            background.paste(mockup, mask=mockup.split()[-1])  # Используем альфа-канал как маску
            mockup = background
        elif mockup.mode != 'RGB':
            mockup = mockup.convert('RGB')
        
        # Улучшение базового изображения
        mockup = self.enhance_product_image(mockup)
        
        return mockup
    
    def enhance_product_image(self, image: Image.Image) -> Image.Image:
        """Улучшение изображения товара для мокапа"""
        # Убеждаемся, что изображение в RGB режиме
        if image.mode == 'RGBA':
            # Создаем белый фон для RGBA изображений
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Улучшение контраста и яркости
        image = ImageOps.autocontrast(image, cutoff=1)
        
        # Добавление легкого шарпа для четкости
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
        
        # Легкое улучшение насыщенности
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def integrate_logo(self, mockup: Image.Image, logo_image: Image.Image, position: str) -> Image.Image:
        """Интеграция логотипа в мокап"""
        # Подготовка логотипа с эффектами
        logo = self.create_enhanced_logo(logo_image)
        
        # Позиционирование логотипа
        if position == "center":
            x = (mockup.width - logo.width) // 2
            y = (mockup.height - logo.height) // 2
        elif position == "top-right":
            x = mockup.width - logo.width - 20
            y = 20
        elif position == "bottom-left":
            x = 20
            y = mockup.height - logo.height - 20
        else:
            x = (mockup.width - logo.width) // 2
            y = (mockup.height - logo.height) // 2
        
        # Наложение логотипа с эффектами и реалистичной интеграцией
        if logo.mode == 'RGBA':
            # Создаем маску для более мягкого наложения
            mask = logo.split()[-1]
            # Применяем логотип с прозрачностью для более реалистичного вида
            mockup.paste(logo, (x, y), mask)
        else:
            mockup.paste(logo, (x, y))
        
        # Добавляем эффекты для более реалистичной интеграции
        mockup = self.add_realistic_integration_effects(mockup, x, y, logo.width, logo.height)
        
        # Финальные эффекты для интеграции
        mockup = self.add_integration_effects(mockup)
        
        return mockup
    
    def create_enhanced_logo(self, logo_image: Image.Image) -> Image.Image:
        """Создание улучшенного логотипа с эффектами вышивки/печати"""
        # Конвертация в RGBA для работы с прозрачностью
        if logo_image.mode != 'RGBA':
            logo_image = logo_image.convert('RGBA')
        
        # Создание эффекта вышивки/печати
        enhanced_logo = logo_image.copy()
        
        # Добавление легкого размытия для эффекта ткани
        enhanced_logo = enhanced_logo.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Увеличение контраста для лучшей видимости (только для RGB каналов)
        # Создаем временную RGB версию для autocontrast
        rgb_logo = Image.new('RGB', enhanced_logo.size, (255, 255, 255))
        rgb_logo.paste(enhanced_logo, mask=enhanced_logo.split()[-1])
        rgb_logo = ImageOps.autocontrast(rgb_logo, cutoff=2)
        
        # Конвертируем обратно в RGBA
        enhanced_logo = rgb_logo.convert('RGBA')
        
        # Возвращаем RGBA для правильного наложения
        return enhanced_logo
    
    def add_integration_effects(self, image: Image.Image) -> Image.Image:
        """Добавление эффектов для интеграции логотипа"""
        # Убеждаемся, что изображение в RGB режиме
        if image.mode == 'RGBA':
            # Создаем белый фон для RGBA изображений
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Легкое улучшение контраста
        image = ImageOps.autocontrast(image, cutoff=1)
        
        # Добавление легкого шарпа для четкости
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return image
    
    def add_realistic_integration_effects(self, image: Image.Image, logo_x: int, logo_y: int, logo_w: int, logo_h: int) -> Image.Image:
        """Добавление реалистичных эффектов интеграции логотипа"""
        # Создаем копию для работы
        result = image.copy()
        
        # Добавляем легкое размытие краев логотипа для более мягкой интеграции
        # Создаем маску для области логотипа
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rectangle([logo_x, logo_y, logo_x + logo_w, logo_y + logo_h], fill=255)
        
        # Применяем легкое размытие к области логотипа
        blurred = result.filter(ImageFilter.GaussianBlur(radius=0.5))
        result = Image.composite(blurred, result, mask)
        
        # Добавляем легкие тени вокруг логотипа
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Рисуем тень с небольшим смещением
        shadow_draw.rectangle([logo_x + 2, logo_y + 2, logo_x + logo_w + 2, logo_y + logo_h + 2], fill=(0, 0, 0, 30))
        
        # Накладываем тень
        result = Image.alpha_composite(result.convert('RGBA'), shadow).convert('RGB')
        
        return result
    
    def add_mockup_effects(self, image: Image.Image) -> Image.Image:
        """Добавление эффектов для более реалистичного мокапа"""
        # Убеждаемся, что изображение в RGB режиме
        if image.mode == 'RGBA':
            # Создаем белый фон для RGBA изображений
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Легкое улучшение контраста
        image = ImageOps.autocontrast(image, cutoff=1)
        
        # Добавление легкого шарпа для четкости
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return image
