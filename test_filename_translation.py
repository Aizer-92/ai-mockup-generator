#!/usr/bin/env python3
"""
Тест перевода названий файлов
"""

from ftp_uploader import FTPUploader

def test_filename_translation():
    """Тестирует перевод русских названий в английские"""
    print("🔤 Тест перевода названий файлов")
    print("================================")
    
    # Создаем экземпляр загрузчика
    uploader = FTPUploader("test", "test", "test")
    
    # Тестовые названия
    test_names = [
        "Классический",
        "Современный",
        "Вышивка",
        "Центр",
        "Неизвестно",
        "Спортивный стиль",
        "Русские символы: привет!",
        "Mixed English/Русский текст",
        "",
        "123456789012345678901234567890"  # Длинное название
    ]
    
    print("Тестирование перевода названий:")
    for name in test_names:
        translated = uploader._translate_style_name(name)
        print(f"  '{name}' → '{translated}'")
    
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_filename_translation()
