# ⚡ Быстрая настройка сервера

## Подключение к серверу

```bash
ssh search.headcorn.pro
# Введите пароль
```

## Копируйте и вставляйте команды по порядку:

### 1. Создание папки для мокапов

```bash
sudo mkdir -p /var/www/html/mockups
sudo chmod 755 /var/www/html/mockups
sudo chown www-data:www-data /var/www/html/mockups
ls -la /var/www/html/mockups
```

### 2. Настройка Apache

```bash
sudo tee /etc/apache2/sites-available/mockups.conf > /dev/null << 'EOF'
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
EOF
```

### 3. Включение модулей и сайта

```bash
sudo a2enmod headers
sudo a2enmod rewrite
sudo a2ensite mockups.conf
sudo systemctl reload apache2
```

### 4. Настройка FTP

```bash
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
```

### 5. Создание тестового файла

```bash
sudo tee /var/www/html/mockups/test_mockup.json > /dev/null << 'EOF'
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
EOF

sudo chown www-data:www-data /var/www/html/mockups/test_mockup.json
```

### 6. Проверка настройки

```bash
ls -la /var/www/html/mockups
sudo systemctl is-active apache2
sudo systemctl is-active vsftpd
curl -s -o /dev/null -w "HTTP код: %{http_code}" http://localhost/mockups/
```

## Проверка с локального компьютера

```bash
curl http://search.headcorn.pro/mockups/
```

## Настройка Streamlit Secrets

Добавьте в настройки Streamlit Cloud:

```toml
FTP_ENABLED = true
FTP_HOST = "search.headcorn.pro"
FTP_USERNAME = "victoruk_search"
FTP_PASSWORD = "L2F&A#3zVpCq*T"
FTP_REMOTE_PATH = "/var/www/html/mockups"
```

## Готово! 🎉

После выполнения всех команд:
- ✅ Папка `/var/www/html/mockups` создана
- ✅ Apache настроен для доступа к папке
- ✅ FTP работает
- ✅ Веб-доступ: `http://search.headcorn.pro/mockups/`
- ✅ CORS настроен для Streamlit

Теперь мокапы будут автоматически загружаться на ваш сервер из Streamlit приложения!
