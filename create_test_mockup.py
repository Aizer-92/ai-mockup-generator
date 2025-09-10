#!/usr/bin/env python3
"""
Создание тестового мокапа для проверки галереи
"""

import ftplib
import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def create_test_mockup():
    """Создает тестовый мокап и загружает на FTP сервер"""
    print("🎨 Создание тестового мокапа")
    print("============================")
    
    try:
        # Создаем тестовое изображение
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(image)
        
        # Добавляем текст
        try:
            # Пытаемся использовать системный шрифт
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            # Fallback на стандартный шрифт
            font = ImageFont.load_default()
        
        text = "Тестовый мокап\nAI Mockup Generator\n2024"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='darkblue', font=font)
        
        # Добавляем рамку
        draw.rectangle([10, 10, width-10, height-10], outline='darkblue', width=3)
        
        # Сохраняем в байты
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_data = img_buffer.getvalue()
        
        print(f"✅ Тестовое изображение создано: {len(img_data)} байт")
        
        # Создаем метаданные
        metadata = {
            "mockup_style": "Тестовый стиль",
            "logo_application": "Тестовое нанесение",
            "logo_placement": "Центр",
            "logo_size": "Средний",
            "logo_color": "Темно-синий",
            "product_color": "Светло-голубой",
            "product_angle": "Прямой",
            "special_requirements": "Тестовый мокап для проверки галереи"
        }
        
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Переходим в папку mockups
        ftp.cwd('/public_html/mockups')
        print("✅ Перешли в папку mockups")
        
        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"test_mockup_{timestamp}.jpg"
        json_filename = f"test_mockup_{timestamp}.json"
        
        # Загружаем изображение
        img_buffer = io.BytesIO(img_data)
        ftp.storbinary(f'STOR {image_filename}', img_buffer)
        print(f"✅ Изображение загружено: {image_filename}")
        
        # Загружаем метаданные
        json_data = {
            "filename": image_filename,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "source": "test_creation"
        }
        
        json_buffer = io.BytesIO(json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8'))
        ftp.storbinary(f'STOR {json_filename}', json_buffer)
        print(f"✅ Метаданные загружены: {json_filename}")
        
        # Показываем содержимое папки
        print("\n📁 Содержимое папки mockups:")
        contents = []
        ftp.retrlines('LIST', contents.append)
        
        for item in contents:
            print(f"  {item}")
        
        ftp.quit()
        
        # Проверяем веб-доступ
        web_url = f"http://search.headcorn.pro/mockups/{image_filename}"
        print(f"\n🌐 Веб-доступ: {web_url}")
        
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
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    create_test_mockup()
