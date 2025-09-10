# 🔑 Настройка SSH ключа для автоматического подключения

## Обзор

Если на FTP сервере лежит SSH ключ, можно настроить автоматическое подключение без ввода пароля.

## 🚀 Быстрая настройка

### 1. Скачайте SSH ключ с FTP сервера

#### Вариант 1: Через веб-интерфейс
1. Откройте браузер
2. Перейдите на `http://search.headcorn.pro/`
3. Найдите файл с SSH ключом (обычно `id_rsa` или `id_rsa.pub`)
4. Скачайте его на локальный компьютер

#### Вариант 2: Через FTP клиент
1. Установите FileZilla или другой FTP клиент
2. Подключитесь к серверу:
   - **Host**: `search.headcorn.pro`
   - **Username**: `victoruk_search`
   - **Password**: `L2F&A#3zVpCq*T`
3. Найдите файл с SSH ключом
4. Скачайте его на локальный компьютер

#### Вариант 3: Через curl (если ключ доступен по HTTP)
```bash
# Скачиваем приватный ключ
curl -o ~/.ssh/id_rsa http://search.headcorn.pro/id_rsa

# Устанавливаем права
chmod 600 ~/.ssh/id_rsa
```

### 2. Настройте SSH ключ

```bash
# Создаем директорию для SSH ключей
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Копируем ключ в правильное место
cp /path/to/downloaded/key ~/.ssh/id_rsa

# Устанавливаем правильные права
chmod 600 ~/.ssh/id_rsa
```

### 3. Настройте SSH конфигурацию

```bash
# Создаем SSH конфигурацию
cat >> ~/.ssh/config << 'EOF'

# Конфигурация для search.headcorn.pro
Host search.headcorn.pro
    HostName search.headcorn.pro
    User bakirovresad
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

# Устанавливаем права
chmod 600 ~/.ssh/config
```

### 4. Тестируем SSH подключение

```bash
# Тестируем подключение
ssh search.headcorn.pro "echo 'SSH подключение работает'"
```

## 🔧 Автоматическая настройка

### Используйте готовые скрипты:

```bash
# 1. Настройте SSH ключ
./setup_ssh_key.sh

# 2. Запустите автоматическую настройку сервера
./auto_setup_with_ssh.sh
```

## 📋 Проверка настройки

### Проверьте SSH ключ:
```bash
ls -la ~/.ssh/id_rsa
# Должно показать: -rw------- (600)
```

### Проверьте SSH конфигурацию:
```bash
cat ~/.ssh/config
```

### Проверьте SSH подключение:
```bash
ssh search.headcorn.pro "echo 'Тест подключения'"
```

## 🚨 Устранение неполадок

### Ошибка "Permission denied (publickey)":
```bash
# Проверьте права доступа к ключу
chmod 600 ~/.ssh/id_rsa

# Проверьте содержимое ключа
head -1 ~/.ssh/id_rsa
# Должно начинаться с: -----BEGIN OPENSSH PRIVATE KEY-----
```

### Ошибка "No such file or directory":
```bash
# Проверьте, что ключ существует
ls -la ~/.ssh/id_rsa

# Если нет, скачайте его снова
```

### Ошибка "Host key verification failed":
```bash
# Очистите известные хосты
ssh-keygen -R search.headcorn.pro

# Или добавьте в конфигурацию:
# StrictHostKeyChecking no
```

## 🎯 После настройки SSH ключа

### Запустите автоматическую настройку сервера:

```bash
./auto_setup_with_ssh.sh
```

Этот скрипт автоматически:
- ✅ Создаст папку `/var/www/html/mockups`
- ✅ Настроит Apache с CORS
- ✅ Запустит FTP сервис
- ✅ Создаст тестовый файл
- ✅ Проверит все настройки

## 📝 Настройка Streamlit Secrets

После настройки сервера добавьте в Streamlit Secrets:

```toml
FTP_ENABLED = true
FTP_HOST = "search.headcorn.pro"
FTP_USERNAME = "victoruk_search"
FTP_PASSWORD = "L2F&A#3zVpCq*T"
FTP_REMOTE_PATH = "/var/www/html/mockups"
```

## 🎉 Готово!

После настройки SSH ключа:
- ✅ Автоматическое подключение к серверу
- ✅ Никаких паролей при SSH подключении
- ✅ Автоматическая настройка сервера
- ✅ Готовность к загрузке мокапов

## 🔗 Полезные ссылки

- **SSH ключи**: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- **SSH конфигурация**: https://linuxize.com/post/using-the-ssh-config-file/
- **FileZilla**: https://filezilla-project.org/
