#!/usr/bin/env python3
"""
Очистка локальных файлов от старых мокапов
"""

import os
import shutil

def clean_local_files():
    """Очищает локальные папки от старых мокапов"""
    print("🧹 Очистка локальных файлов")
    print("==========================")
    
    # Папки для очистки
    folders_to_clean = ['outputs', 'cache', 'uploads']
    
    total_deleted = 0
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"\n📁 Очистка папки: {folder}")
            
            # Получаем список файлов
            files = os.listdir(folder)
            print(f"   Найдено файлов: {len(files)}")
            
            # Удаляем все файлы
            for file in files:
                file_path = os.path.join(folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"   ✅ Удален: {file}")
                        total_deleted += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"   ✅ Удалена папка: {file}")
                        total_deleted += 1
                except Exception as e:
                    print(f"   ❌ Ошибка удаления {file}: {e}")
        else:
            print(f"\n📁 Папка не существует: {folder}")
    
    print(f"\n🎉 Очистка завершена!")
    print(f"   Удалено файлов/папок: {total_deleted}")
    
    # Проверяем результат
    print(f"\n📊 Состояние папок:")
    for folder in folders_to_clean:
        if os.path.exists(folder):
            files = os.listdir(folder)
            print(f"   {folder}: {len(files)} файлов")
        else:
            print(f"   {folder}: не существует")

if __name__ == "__main__":
    clean_local_files()
