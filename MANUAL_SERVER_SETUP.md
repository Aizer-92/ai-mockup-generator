# 🖥️ Ручная настройка сервера через SSH

## Подключение к серверу

```bash
ssh search.headcorn.pro
# Введите пароль когда попросит
```

## 1. Создание папки для мокапов

```bash
# Создаем папку
sudo mkdir -p /var/www/html/mockups

# Устанавливаем права доступа
sudo chmod 755 /var/www/html/mockups
sudo chown www-data:www-data /var/www/html/mockups

# Проверяем создание
ls -la /var/www/html/mockups
```

## 2. Настройка Apache

### Создаем конфигурацию для мокапов:

```bash
sudo nano /etc/apache2/sites-available/mockups.conf
```

### Добавьте следующее содержимое:

```apache
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
```

### Включаем модули и сайт:

```bash
# Включаем необходимые модули
sudo a2enmod headers
sudo a2enmod rewrite

# Включаем сайт
sudo a2ensite mockups.conf

# Перезапускаем Apache
sudo systemctl reload apache2
```

## 3. Проверка FTP

```bash
# Проверяем FTP сервис
systemctl status vsftpd
# или
systemctl status proftpd

# Если FTP не активен, запускаем
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
```

## 4. Создание тестового файла

```bash
# Создаем тестовый файл
cat > /var/www/html/mockups/test_mockup.json << 'EOF'
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

# Устанавливаем права
sudo chown www-data:www-data /var/www/html/mockups/test_mockup.json
```

## 5. Проверка настройки

### Проверяем веб-доступ:

```bash
# Проверяем локально
curl http://localhost/mockups/

# Проверяем снаружи
curl http://search.headcorn.pro/mockups/
```

### Проверяем права доступа:

```bash
ls -la /var/www/html/mockups
```

## 6. Настройка файрвола (если нужно)

```bash
# Разрешаем HTTP и HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Разрешаем FTP
sudo ufw allow 21

# Проверяем статус
sudo ufw status
```

## 7. Проверка логов

```bash
# Логи Apache
sudo tail -f /var/log/apache2/mockups_error.log
sudo tail -f /var/log/apache2/mockups_access.log

# Логи FTP
sudo tail -f /var/log/vsftpd.log
```

## 8. Тестирование FTP

### С локального компьютера:

```bash
# Тестируем FTP подключение
ftp search.headcorn.pro
# Username: victoruk_search
# Password: L2F&A#3zVpCq*T

# В FTP сессии:
cd /var/www/html/mockups
ls
put test_file.txt
quit
```

## 9. Финальная проверка

### Проверяем все компоненты:

```bash
# 1. Папка существует
ls -la /var/www/html/mockups

# 2. Apache работает
sudo systemctl status apache2

# 3. FTP работает
sudo systemctl status vsftpd

# 4. Веб-доступ работает
curl -I http://search.headcorn.pro/mockups/

# 5. Права доступа правильные
ls -la /var/www/html/mockups
```

## 10. Настройка для Streamlit

### Добавьте в Streamlit Secrets:

```toml
FTP_ENABLED = true
FTP_HOST = "search.headcorn.pro"
FTP_USERNAME = "victoruk_search"
FTP_PASSWORD = "L2F&A#3zVpCq*T"
FTP_REMOTE_PATH = "/var/www/html/mockups"
```

## 🎉 Готово!

После выполнения всех шагов:

- ✅ Папка `/var/www/html/mockups` создана
- ✅ Apache настроен для доступа к папке
- ✅ FTP работает
- ✅ Веб-доступ: `http://search.headcorn.pro/mockups/`
- ✅ CORS настроен для Streamlit
- ✅ Права доступа установлены

## 🔧 Устранение неполадок

### Ошибка "Permission denied":
```bash
sudo chown -R www-data:www-data /var/www/html/mockups
sudo chmod -R 755 /var/www/html/mockups
```

### Ошибка "Apache not found":
```bash
sudo apt update
sudo apt install apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```

### Ошибка "FTP not working":
```bash
sudo apt install vsftpd
sudo systemctl start vsftpd
sudo systemctl enable vsftpd
```

### Ошибка "CORS not working":
```bash
sudo a2enmod headers
sudo systemctl reload apache2
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи Apache: `sudo tail -f /var/log/apache2/error.log`
2. Проверьте статус сервисов: `sudo systemctl status apache2 vsftpd`
3. Проверьте права доступа: `ls -la /var/www/html/mockups`
4. Проверьте файрвол: `sudo ufw status`
