#!/usr/bin/env python3
"""
Проверка папки public_html на FTP сервере
"""

import ftplib
import os
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def check_public_html():
    """Проверяет папку public_html"""
    print("🔍 Проверка папки public_html...")
    
    try:
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Переходим в public_html
        ftp.cwd('/public_html')
        print("✅ Перешли в /public_html")
        
        # Получаем список файлов
        print("\n📁 Содержимое public_html:")
        contents = []
        ftp.retrlines('LIST', contents.append)
        
        for item in contents:
            print(f"  {item}")
        
        # Пробуем создать папку mockups
        print("\n🔧 Попытка создать папку mockups...")
        try:
            ftp.mkd('mockups')
            print("✅ Папка mockups создана")
        except Exception as e:
            print(f"❌ Не удалось создать папку mockups: {e}")
        
        # Проверяем, есть ли уже папка mockups
        print("\n🔍 Проверка папки mockups...")
        try:
            ftp.cwd('mockups')
            print("✅ Папка mockups существует")
            
            # Показываем содержимое
            mockup_contents = []
            ftp.retrlines('LIST', mockup_contents.append)
            print(f"   Содержимое: {len(mockup_contents)} элементов")
            
            for item in mockup_contents:
                print(f"     {item}")
                
        except Exception as e:
            print(f"❌ Папка mockups не существует: {e}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка FTP: {e}")
        return False

if __name__ == "__main__":
    check_public_html()
