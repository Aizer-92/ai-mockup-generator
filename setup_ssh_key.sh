#!/bin/bash

# Настройка SSH ключа для автоматического подключения
# Запуск: ./setup_ssh_key.sh

echo "🔑 Настройка SSH ключа для автоматического подключения"
echo "======================================================"

# Создаем директорию для SSH ключей
mkdir -p ~/.ssh
chmod 700 ~/.ssh

echo ""
echo "📁 Создана директория ~/.ssh"

# Проверяем, есть ли уже ключ
if [ -f ~/.ssh/id_rsa ]; then
    echo "⚠️ SSH ключ уже существует: ~/.ssh/id_rsa"
    echo "Хотите заменить его? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🔄 Заменяем существующий ключ..."
    else
        echo "❌ Отменено"
        exit 0
    fi
fi

echo ""
echo "📝 Инструкция по настройке SSH ключа:"
echo ""
echo "1. Скачайте SSH ключ с FTP сервера:"
echo "   - Подключитесь к FTP: search.headcorn.pro"
echo "   - Пользователь: victoruk_search"
echo "   - Пароль: L2F&A#3zVpCq*T"
echo "   - Найдите файл с SSH ключом (обычно id_rsa или id_rsa.pub)"
echo "   - Скачайте его на локальный компьютер"
echo ""
echo "2. Поместите ключ в правильное место:"
echo "   - Если это приватный ключ (id_rsa):"
echo "     cp /path/to/downloaded/key ~/.ssh/id_rsa"
echo "     chmod 600 ~/.ssh/id_rsa"
echo "   - Если это публичный ключ (id_rsa.pub):"
echo "     cp /path/to/downloaded/key ~/.ssh/id_rsa.pub"
echo "     chmod 644 ~/.ssh/id_rsa.pub"
echo ""
echo "3. Запустите этот скрипт снова:"
echo "   ./setup_ssh_key.sh"
echo ""

# Проверяем, есть ли ключ после инструкции
if [ -f ~/.ssh/id_rsa ]; then
    echo "✅ SSH ключ найден: ~/.ssh/id_rsa"
    
    # Устанавливаем правильные права
    chmod 600 ~/.ssh/id_rsa
    
    echo "🔧 Настраиваем SSH конфигурацию..."
    
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
    
    chmod 600 ~/.ssh/config
    
    echo "✅ SSH конфигурация создана"
    
    echo ""
    echo "🧪 Тестируем SSH подключение..."
    
    # Тестируем подключение
    if ssh -o ConnectTimeout=10 search.headcorn.pro "echo 'SSH подключение работает'"; then
        echo "✅ SSH подключение работает!"
        echo ""
        echo "🎉 Настройка завершена!"
        echo "Теперь можно запустить автоматическую настройку сервера:"
        echo "   ./auto_setup_server.sh"
    else
        echo "❌ SSH подключение не работает"
        echo "Проверьте:"
        echo "1. Правильность SSH ключа"
        echo "2. Права доступа к файлу (~/.ssh/id_rsa)"
        echo "3. Настройки SSH сервера"
    fi
    
else
    echo "❌ SSH ключ не найден в ~/.ssh/id_rsa"
    echo "Следуйте инструкции выше для скачивания и настройки ключа"
fi

echo ""
echo "📋 Альтернативные способы скачивания ключа:"
echo ""
echo "1. Через веб-интерфейс FTP (если доступен):"
echo "   http://search.headcorn.pro/"
echo ""
echo "2. Через FileZilla или другой FTP клиент:"
echo "   Host: search.headcorn.pro"
echo "   Username: victoruk_search"
echo "   Password: L2F&A#3zVpCq*T"
echo ""
echo "3. Через curl (если ключ доступен по HTTP):"
echo "   curl -o ~/.ssh/id_rsa http://search.headcorn.pro/id_rsa"
echo "   chmod 600 ~/.ssh/id_rsa"
