#!/bin/bash

# Скрипт для настройки сервера через SSH
# Запуск: ./setup_server.sh

echo "🚀 Настройка сервера для AI Mockup Generator"
echo "=============================================="

# Проверяем SSH подключение
echo "🔍 Проверка SSH подключения..."
ssh -o ConnectTimeout=10 search.headcorn.pro "echo 'SSH подключение работает'" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ SSH подключение успешно"
else
    echo "❌ Ошибка SSH подключения"
    echo "📝 Убедитесь, что SSH доступен и пароль правильный"
    exit 1
fi

echo ""
echo "📁 Создание папки для мокапов..."

# Создаем папку для мокапов
ssh search.headcorn.pro << 'EOF'
    echo "Создаем папку /var/www/html/mockups..."
    sudo mkdir -p /var/www/html/mockups
    sudo chmod 755 /var/www/html/mockups
    sudo chown www-data:www-data /var/www/html/mockups
    
    echo "Проверяем создание папки..."
    ls -la /var/www/html/mockups
    
    echo "Создаем тестовый файл..."
    echo "Тестовая папка для AI Mockup Generator" > /var/www/html/mockups/README.txt
    sudo chown www-data:www-data /var/www/html/mockups/README.txt
    
    echo "✅ Папка создана успешно"
EOF

echo ""
echo "🌐 Настройка веб-сервера..."

# Настраиваем Apache
ssh search.headcorn.pro << 'EOF'
    echo "Проверяем Apache конфигурацию..."
    
    # Создаем конфигурацию для мокапов
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

    echo "Включаем модули Apache..."
    sudo a2enmod headers
    sudo a2enmod rewrite
    
    echo "Включаем сайт..."
    sudo a2ensite mockups.conf
    
    echo "Перезапускаем Apache..."
    sudo systemctl reload apache2
    
    echo "✅ Apache настроен"
EOF

echo ""
echo "🔧 Настройка FTP..."

# Настраиваем FTP
ssh search.headcorn.pro << 'EOF'
    echo "Проверяем FTP сервис..."
    
    # Проверяем, что FTP работает
    if systemctl is-active --quiet vsftpd; then
        echo "✅ vsftpd активен"
    elif systemctl is-active --quiet proftpd; then
        echo "✅ proftpd активен"
    else
        echo "⚠️ FTP сервис не найден, но папка доступна через веб"
    fi
    
    echo "Проверяем права доступа к папке..."
    ls -la /var/www/html/mockups
EOF

echo ""
echo "🧪 Тестирование настройки..."

# Тестируем веб-доступ
echo "Проверяем веб-доступ к папке мокапов..."
curl -s -o /dev/null -w "%{http_code}" http://search.headcorn.pro/mockups/

if [ $? -eq 0 ]; then
    echo "✅ Веб-доступ работает"
else
    echo "⚠️ Веб-доступ может не работать, проверьте настройки"
fi

echo ""
echo "📋 Создание тестового файла..."

# Создаем тестовый мокап
ssh search.headcorn.pro << 'EOF'
    echo "Создаем тестовый мокап..."
    
    # Создаем простой тестовый файл
    cat > /var/www/html/mockups/test_mockup.json << 'JSON_EOF'
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
EOF

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
echo "1. Добавьте FTP настройки в Streamlit Secrets"
echo "2. Запустите Streamlit приложение"
echo "3. Сгенерируйте тестовый мокап"
echo "4. Проверьте загрузку в папку /var/www/html/mockups"
