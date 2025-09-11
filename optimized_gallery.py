"""
Оптимизированная галерея мокапов с кэшированием и ленивой загрузкой
"""
import os
import json
import time
import base64
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io
import streamlit as st
from config import FTP_ENABLED, SERVER_STORAGE_ENABLED
from ftp_uploader import get_ftp_uploader
from server_storage import get_server_storage

class OptimizedGallery:
    """Оптимизированная галерея мокапов с кэшированием"""
    
    def __init__(self):
        """Инициализация галереи"""
        self.cache_key = "gallery_cache"
        self.cache_expiry = 300  # 5 минут
        self.thumbnail_size = (200, 200)
        self.max_images_per_page = 20
        
    def get_cached_mockups(self) -> Optional[List[Dict]]:
        """Получает кэшированный список мокапов"""
        if self.cache_key in st.session_state:
            cache_data = st.session_state[self.cache_key]
            if time.time() - cache_data['timestamp'] < self.cache_expiry:
                return cache_data['mockups']
        return None
    
    def cache_mockups(self, mockups: List[Dict]):
        """Кэширует список мокапов"""
        st.session_state[self.cache_key] = {
            'mockups': mockups,
            'timestamp': time.time()
        }
    
    def get_all_mockups(self, limit: int = 100) -> List[Dict]:
        """Получает все мокапы из всех источников с кэшированием"""
        # Проверяем кэш
        cached_mockups = self.get_cached_mockups()
        if cached_mockups is not None:
            return cached_mockups[:limit]
        
        all_mockups = []
        
        # Получаем мокапы с FTP сервера
        if FTP_ENABLED:
            ftp_mockups = self.get_ftp_mockups_optimized(limit // 2)
            all_mockups.extend(ftp_mockups)
        
        # Получаем мокапы с сервера
        if SERVER_STORAGE_ENABLED:
            server_mockups = self.get_server_mockups_optimized(limit // 2)
            all_mockups.extend(server_mockups)
        
        # Google Drive отключен
        
        # Сортируем по дате создания
        all_mockups.sort(key=lambda x: x.get('created_time', 0), reverse=True)
        
        # Кэшируем результат
        self.cache_mockups(all_mockups)
        
        return all_mockups[:limit]
    
    def get_ftp_mockups_optimized(self, limit: int = 50) -> List[Dict]:
        """Оптимизированное получение мокапов с FTP"""
        try:
            ftp_uploader = get_ftp_uploader()
            if not ftp_uploader:
                return []
            
            mockups = ftp_uploader.list_files()
            
            # Ограничиваем количество и добавляем оптимизированные данные
            optimized_mockups = []
            for i, mockup in enumerate(mockups[:limit]):
                optimized_mockup = {
                    'id': mockup['filename'].replace('.jpg', ''),
                    'filename': mockup['filename'],
                    'web_url': mockup['web_url'],
                    'metadata': mockup.get('metadata', {}),
                    'created_time': self._extract_timestamp_from_filename(mockup['filename']),
                    'source': 'ftp',
                    'thumbnail_url': mockup['web_url'],  # Используем оригинальное изображение как thumbnail
                    'size_optimized': True
                }
                optimized_mockups.append(optimized_mockup)
            
            return optimized_mockups
            
        except Exception as e:
            st.error(f"Ошибка получения мокапов с FTP: {e}")
            return []
    
    def get_server_mockups_optimized(self, limit: int = 50) -> List[Dict]:
        """Оптимизированное получение мокапов с сервера"""
        try:
            server_storage = get_server_storage()
            mockups = server_storage.get_mockups_list(limit)
            
            # Оптимизируем данные
            optimized_mockups = []
            for mockup in mockups:
                optimized_mockup = {
                    'id': mockup['id'],
                    'filename': mockup['filename'],
                    'web_url': mockup['web_url'],
                    'metadata': mockup.get('metadata', {}),
                    'created_time': mockup.get('created_time', 0),
                    'source': 'server',
                    'thumbnail_url': mockup['web_url'],
                    'size_optimized': True
                }
                optimized_mockups.append(optimized_mockup)
            
            return optimized_mockups
            
        except Exception as e:
            st.error(f"Ошибка получения мокапов с сервера: {e}")
            return []
    
    # Google Drive функции удалены
    
    def _extract_timestamp_from_filename(self, filename: str) -> float:
        """Извлекает timestamp из имени файла"""
        try:
            # Формат: mockup_20241201_123456_style.jpg
            parts = filename.split('_')
            if len(parts) >= 3:
                date_part = parts[1]  # 20241201
                time_part = parts[2]  # 123456
                datetime_str = f"{date_part}_{time_part}"
                dt = time.strptime(datetime_str, "%Y%m%d_%H%M%S")
                return time.mktime(dt)
        except:
            pass
        return time.time()
    
    def display_gallery(self, mockups: List[Dict], page: int = 0):
        """Отображает галерею мокапов с пагинацией"""
        if not mockups:
            st.info("📁 Галерея пока пуста. Сгенерируйте несколько мокапов, чтобы увидеть их здесь!")
            return
        
        # Пагинация
        start_idx = page * self.max_images_per_page
        end_idx = start_idx + self.max_images_per_page
        page_mockups = mockups[start_idx:end_idx]
        
        # Отображаем мокапы в сетке
        cols_per_row = 4
        for i in range(0, len(page_mockups), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(page_mockups):
                    mockup = page_mockups[i + j]
                    self._display_mockup_card(col, mockup)
        
        # Навигация по страницам
        total_pages = (len(mockups) - 1) // self.max_images_per_page + 1
        if total_pages > 1:
            self._display_pagination(page, total_pages)
    
    def _display_mockup_card(self, col, mockup: Dict):
        """Отображает карточку мокапа"""
        with col:
            try:
                # Отображаем изображение
                st.image(
                    mockup['web_url'],
                    caption=mockup['filename'],
                    use_column_width=True,
                    width=200
                )
                
                # Метаданные
                metadata = mockup.get('metadata', {})
                style = metadata.get('mockup_style', 'Неизвестно')
                application = metadata.get('logo_application', 'Неизвестно')
                
                st.caption(f"**Стиль:** {style}")
                st.caption(f"**Нанесение:** {application}")
                st.caption(f"**Источник:** {mockup['source']}")
                
                # Кнопка удаления
                if st.button("🗑️", key=f"delete_{mockup['id']}", help="Удалить мокап"):
                    self._delete_mockup(mockup)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Ошибка отображения мокапа: {e}")
    
    def _display_pagination(self, current_page: int, total_pages: int):
        """Отображает пагинацию"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_page > 0:
                if st.button("⬅️ Предыдущая"):
                    st.session_state['gallery_page'] = current_page - 1
                    st.rerun()
        
        with col2:
            st.write(f"Страница {current_page + 1} из {total_pages}")
        
        with col3:
            if current_page < total_pages - 1:
                if st.button("Следующая ➡️"):
                    st.session_state['gallery_page'] = current_page + 1
                    st.rerun()
    
    def _delete_mockup(self, mockup: Dict):
        """Удаляет мокап"""
        try:
            if mockup['source'] == 'ftp':
                ftp_uploader = get_ftp_uploader()
                if ftp_uploader:
                    ftp_uploader.delete_file(mockup['filename'])
            elif mockup['source'] == 'server':
                server_storage = get_server_storage()
                server_storage.delete_mockup(mockup['filename'])
            
            # Очищаем кэш
            if self.cache_key in st.session_state:
                del st.session_state[self.cache_key]
            
            st.success(f"Мокап {mockup['filename']} удален")
            
        except Exception as e:
            st.error(f"Ошибка удаления мокапа: {e}")
    
    def apply_filters(self, mockups: List[Dict], 
                     style_filter: str = "Все",
                     application_filter: str = "Все",
                     date_filter: str = "Все") -> List[Dict]:
        """Применяет фильтры к списку мокапов"""
        filtered = mockups
        
        # Фильтр по стилю
        if style_filter != "Все":
            filtered = [m for m in filtered 
                       if m.get('metadata', {}).get('mockup_style') == style_filter]
        
        # Фильтр по типу нанесения
        if application_filter != "Все":
            filtered = [m for m in filtered 
                       if m.get('metadata', {}).get('logo_application') == application_filter]
        
        # Фильтр по дате
        if date_filter != "Все":
            from datetime import datetime, timedelta
            now = datetime.now()
            
            if date_filter == "Сегодня":
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_filter == "За неделю":
                cutoff = now - timedelta(days=7)
            elif date_filter == "За месяц":
                cutoff = now - timedelta(days=30)
            
            filtered = [m for m in filtered 
                       if datetime.fromtimestamp(m.get('created_time', 0)) >= cutoff]
        
        return filtered
    
    def get_filter_options(self, mockups: List[Dict]) -> Tuple[List[str], List[str]]:
        """Получает опции для фильтров"""
        styles = set()
        applications = set()
        
        for mockup in mockups:
            metadata = mockup.get('metadata', {})
            styles.add(metadata.get('mockup_style', 'Неизвестно'))
            applications.add(metadata.get('logo_application', 'Неизвестно'))
        
        return sorted(list(styles)), sorted(list(applications))

def get_optimized_gallery() -> OptimizedGallery:
    """Получает экземпляр оптимизированной галереи"""
    return OptimizedGallery()