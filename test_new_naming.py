#!/usr/bin/env python3
"""
Тест новой системы именования файлов
"""

import ftplib
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from dotenv import load_dotenv
from ftp_uploader import FTPUploader

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def test_new_naming():
    """Тестирует новую систему именования файлов"""
    print("🧪 Тест новой системы именования")
    print("===============================")
    
    try:
        # Создаем FTP загрузчик
        uploader = FTPUploader(
            os.getenv('FTP_HOST'),
            os.getenv('FTP_USERNAME'),
            os.getenv('FTP_PASSWORD'),
            os.getenv('FTP_REMOTE_PATH')
        )
        
        # Тестируем подключение
        if not uploader.test_connection():
            print("❌ FTP подключение не работает")
            return False
        
        # Создаем тестовое изображение
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='lightgreen')
        draw = ImageDraw.Draw(image)
        
        # Добавляем текст
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "New Naming System\nAI Mockup Generator\nEnglish Names Only"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='darkgreen', font=font)
        draw.rectangle([10, 10, width-10, height-10], outline='darkgreen', width=3)
        
        # Сохраняем в байты
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_data = img_buffer.getvalue()
        
        print(f"✅ Тестовое изображение создано: {len(img_data)} байт")
        
        # Создаем метаданные с русскими названиями
        metadata = {
            "mockup_style": "Современный",
            "logo_application": "Вышивка",
            "logo_placement": "Центр",
            "logo_size": "Средний",
            "logo_color": "Зеленый",
            "product_color": "Светло-зеленый",
            "product_angle": "Прямой",
            "special_requirements": "Тест новой системы именования"
        }
        
        # Загружаем мокап
        filename = uploader.upload_mockup(img_data, metadata, "Тест новой системы именования")
        
        if filename:
            print(f"✅ Мокап загружен: {filename}")
            
            # Проверяем веб-доступ
            web_url = f"http://search.headcorn.pro/mockups/{filename}"
            print(f"🌐 Веб-доступ: {web_url}")
            
            try:
                import requests
                response = requests.get(web_url, timeout=10)
                if response.status_code == 200:
                    print("✅ Изображение доступно через веб")
                else:
                    print(f"❌ Изображение недоступно: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка проверки веб-доступа: {e}")
            
            return True
        else:
            print("❌ Ошибка загрузки мокапа")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_new_naming()
