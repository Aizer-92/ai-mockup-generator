#!/bin/bash

# Настройка сервера с паролем (улучшенная версия)
# Запуск: ./setup_server_password.sh

echo "🚀 Настройка сервера для AI Mockup Generator"
echo "=============================================="
echo ""
echo "📝 Вам потребуется ввести пароль SSH"
echo ""

# Выполняем все команды одной SSH сессией
ssh -l victoruk_search search.headcorn.pro << 'EOF'
    echo "📁 Создание папки для мокапов..."
    sudo mkdir -p /var/www/html/mockups
    sudo chmod 755 /var/www/html/mockups
    sudo chown www-data:www-data /var/www/html/mockups
    echo "✅ Папка создана: /var/www/html/mockups"
    
    echo ""
    echo "🌐 Настройка Apache..."
    
    # Создаем конфигурацию Apache
    sudo tee /etc/apache2/sites-available/mockups.conf > /dev/null << 'APACHE_EOF'
<VirtualHost *:80>
    ServerName search.headcorn.pro
    DocumentRoot /var/www/html
    
    # Папка для мокапов
    Alias /mockups /var/www/html/mockups
    <Directory "/var/www/html/mockups">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
        
        # Разрешаем CORS для Streamlit
        Header always set Access-Control-Allow-Origin "*"
        Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
        Header always set Access-Control-Allow-Headers "Content-Type"
    </Directory>
    
    # Логи
    ErrorLog ${APACHE_LOG_DIR}/mockups_error.log
    CustomLog ${APACHE_LOG_DIR}/mockups_access.log combined
</VirtualHost>
APACHE_EOF
    
    # Включаем модули и сайт
    sudo a2enmod headers
    sudo a2enmod rewrite
    sudo a2ensite mockups.conf
    sudo systemctl reload apache2
    echo "✅ Apache настроен"
    
    echo ""
    echo "🔧 Настройка FTP..."
    sudo systemctl start vsftpd 2>/dev/null || sudo systemctl start proftpd 2>/dev/null || echo "FTP уже запущен"
    sudo systemctl enable vsftpd 2>/dev/null || sudo systemctl enable proftpd 2>/dev/null || echo "FTP уже включен"
    echo "✅ FTP настроен"
    
    echo ""
    echo "🧪 Создание тестового файла..."
    sudo tee /var/www/html/mockups/test_mockup.json > /dev/null << 'JSON_EOF'
{
  "filename": "test_mockup.jpg",
  "metadata": {
    "mockup_style": "Тестовый стиль",
    "logo_application": "Тестовое нанесение",
    "logo_placement": "Центр",
    "test": true
  },
  "created_at": "2024-12-10T14:30:00",
  "source": "server_setup_test"
}
JSON_EOF
    
    sudo chown www-data:www-data /var/www/html/mockups/test_mockup.json
    echo "✅ Тестовый файл создан"
    
    echo ""
    echo "🔍 Проверка настройки..."
    echo "Содержимое папки:"
    ls -la /var/www/html/mockups
    echo ""
    echo "Статус Apache:"
    sudo systemctl is-active apache2
    echo ""
    echo "Статус FTP:"
    sudo systemctl is-active vsftpd || sudo systemctl is-active proftpd
    echo ""
    echo "Тест веб-доступа:"
    curl -s -o /dev/null -w "HTTP код: %{http_code}" http://localhost/mockups/
    echo ""
    echo "✅ Настройка завершена!"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Настройка сервера завершена!"
    echo "=============================================="
    echo ""
    echo "📁 Папка для мокапов: /var/www/html/mockups"
    echo "🌐 Веб-доступ: http://search.headcorn.pro/mockups/"
    echo "🔧 FTP доступ: search.headcorn.pro (пользователь: victoruk_search)"
    echo ""
    echo "✅ Сервер готов для загрузки мокапов из Streamlit приложения"
    echo ""
    echo "📝 Следующие шаги:"
    echo "1. Добавьте FTP настройки в Streamlit Secrets:"
    echo "   FTP_ENABLED = true"
    echo "   FTP_HOST = \"search.headcorn.pro\""
    echo "   FTP_USERNAME = \"victoruk_search\""
    echo "   FTP_PASSWORD = \"L2F&A#3zVpCq*T\""
    echo "   FTP_REMOTE_PATH = \"/var/www/html/mockups\""
    echo ""
    echo "2. Запустите Streamlit приложение"
    echo "3. Сгенерируйте тестовый мокап"
    echo "4. Проверьте загрузку в папку /var/www/html/mockups"
    echo ""
    echo "🔗 Проверьте настройку:"
    echo "   http://search.headcorn.pro/mockups/"
else
    echo ""
    echo "❌ Ошибка настройки сервера"
    echo "Проверьте:"
    echo "1. Правильность пароля SSH"
    echo "2. Доступность сервера"
    echo "3. Права sudo на сервере"
fi
