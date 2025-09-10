#!/bin/bash

# Автоматическая настройка сервера через SSH
# Запуск: ./auto_setup_server.sh

echo "🚀 Автоматическая настройка сервера для AI Mockup Generator"
echo "=========================================================="

# Функция для выполнения команд на сервере
run_ssh_command() {
    local command="$1"
    echo "Выполняем: $command"
    ssh search.headcorn.pro "$command"
}

# Функция для проверки результата
check_result() {
    if [ $? -eq 0 ]; then
        echo "✅ Успешно"
    else
        echo "❌ Ошибка"
        exit 1
    fi
}

echo ""
echo "📁 Создание папки для мокапов..."

# Создаем папку для мокапов
run_ssh_command "sudo mkdir -p /var/www/html/mockups"
check_result

run_ssh_command "sudo chmod 755 /var/www/html/mockups"
check_result

run_ssh_command "sudo chown www-data:www-data /var/www/html/mockups"
check_result

echo ""
echo "🌐 Настройка Apache..."

# Создаем конфигурацию Apache
run_ssh_command "sudo tee /etc/apache2/sites-available/mockups.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName search.headcorn.pro
    DocumentRoot /var/www/html
    
    # Папка для мокапов
    Alias /mockups /var/www/html/mockups
    <Directory \"/var/www/html/mockups\">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
        
        # Разрешаем CORS для Streamlit
        Header always set Access-Control-Allow-Origin \"*\"
        Header always set Access-Control-Allow-Methods \"GET, POST, OPTIONS\"
        Header always set Access-Control-Allow-Headers \"Content-Type\"
    </Directory>
    
    # Логи
    ErrorLog \${APACHE_LOG_DIR}/mockups_error.log
    CustomLog \${APACHE_LOG_DIR}/mockups_access.log combined
</VirtualHost>
EOF"
check_result

# Включаем модули Apache
run_ssh_command "sudo a2enmod headers"
check_result

run_ssh_command "sudo a2enmod rewrite"
check_result

# Включаем сайт
run_ssh_command "sudo a2ensite mockups.conf"
check_result

# Перезапускаем Apache
run_ssh_command "sudo systemctl reload apache2"
check_result

echo ""
echo "🔧 Настройка FTP..."

# Проверяем и запускаем FTP
run_ssh_command "sudo systemctl start vsftpd 2>/dev/null || sudo systemctl start proftpd 2>/dev/null || echo 'FTP уже запущен'"
check_result

run_ssh_command "sudo systemctl enable vsftpd 2>/dev/null || sudo systemctl enable proftpd 2>/dev/null || echo 'FTP уже включен'"
check_result

echo ""
echo "🧪 Создание тестового файла..."

# Создаем тестовый файл
run_ssh_command "sudo tee /var/www/html/mockups/test_mockup.json > /dev/null << 'EOF'
{
  \"filename\": \"test_mockup.jpg\",
  \"metadata\": {
    \"mockup_style\": \"Тестовый стиль\",
    \"logo_application\": \"Тестовое нанесение\",
    \"logo_placement\": \"Центр\",
    \"test\": true
  },
  \"created_at\": \"2024-12-10T14:30:00\",
  \"source\": \"server_setup_test\"
}
EOF"
check_result

run_ssh_command "sudo chown www-data:www-data /var/www/html/mockups/test_mockup.json"
check_result

echo ""
echo "🔍 Проверка настройки..."

# Проверяем папку
run_ssh_command "ls -la /var/www/html/mockups"
check_result

# Проверяем Apache
run_ssh_command "sudo systemctl is-active apache2"
check_result

# Проверяем FTP
run_ssh_command "sudo systemctl is-active vsftpd || sudo systemctl is-active proftpd"
check_result

echo ""
echo "🌐 Тестирование веб-доступа..."

# Тестируем веб-доступ
run_ssh_command "curl -s -o /dev/null -w '%{http_code}' http://localhost/mockups/"
check_result

echo ""
echo "🎉 Настройка сервера завершена!"
echo "=========================================================="
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
