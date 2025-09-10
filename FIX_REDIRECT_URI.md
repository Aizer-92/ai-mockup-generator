# 🔧 Исправление ошибки redirect_uri_mismatch

## Проблема
Ошибка `400: redirect_uri_mismatch` возникает, когда Google OAuth не может найти соответствующий redirect URI в настройках приложения.

## Решение

### 1. Перейдите в Google Cloud Console
1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите проект `quickstart-1591698112539`
3. Перейдите в **APIs & Services** → **Credentials**

### 2. Найдите ваши OAuth 2.0 credentials
1. Найдите запись с Client ID: `1047954485208-849n8mrie4rrapktqodrg6mp4js9r0oi.apps.googleusercontent.com`
2. Нажмите на иконку редактирования (карандаш)

### 3. Добавьте redirect URIs
В разделе **Authorized redirect URIs** добавьте следующие URI:

```
http://localhost:8080
http://localhost:8081
http://localhost:8082
http://localhost:8083
http://localhost:8084
http://localhost:8085
http://localhost:8086
http://localhost:8087
http://localhost:8088
http://localhost:8089
http://localhost:8090
http://localhost:61463
http://localhost:61464
http://localhost:61465
http://localhost:61466
http://localhost:61467
http://localhost:61468
http://localhost:61469
http://localhost:61470
http://localhost:61471
http://localhost:61472
http://localhost:61473
http://localhost:61474
http://localhost:61475
http://localhost:61476
http://localhost:61477
http://localhost:61478
http://localhost:61479
http://localhost:61480
http://localhost:61481
http://localhost:61482
http://localhost:61483
http://localhost:61484
http://localhost:61485
http://localhost:61486
http://localhost:61487
http://localhost:61488
http://localhost:61489
http://localhost:61490
http://localhost:61491
http://localhost:61492
http://localhost:61493
http://localhost:61494
http://localhost:61495
http://localhost:61496
http://localhost:61497
http://localhost:61498
http://localhost:61499
http://localhost:61500
```

### 4. Альтернативное решение (рекомендуется)
Добавьте универсальный redirect URI:

```
http://localhost
```

### 5. Сохраните изменения
1. Нажмите **Save**
2. Подождите 1-2 минуты для применения изменений

## Проверка типа приложения

Убедитесь, что ваше приложение настроено как **Desktop application**, а не **Web application**:

1. В разделе **Application type** должно быть выбрано **Desktop application**
2. Если выбрано **Web application**, создайте новые credentials для Desktop application

## Создание новых credentials (если нужно)

Если текущие credentials не подходят:

1. Нажмите **+ CREATE CREDENTIALS** → **OAuth client ID**
2. Выберите **Desktop application**
3. Дайте название (например: "AI Mockup Generator Desktop")
4. Скачайте новый JSON файл
5. Замените `credentials.json` новым файлом

## Тестирование

После исправления настроек:

1. Удалите файл `token.json` (если существует)
2. Запустите тест снова:
   ```bash
   source venv/bin/activate
   python test_google_drive.py
   ```

## Дополнительные настройки

### OAuth consent screen
Убедитесь, что в **OAuth consent screen**:
1. **User Type**: External
2. **App name**: AI Mockup Generator
3. **User support email**: ваш email
4. **Developer contact**: ваш email
5. **Scopes**: добавлен `https://www.googleapis.com/auth/drive.file`
6. **Test users**: добавлен ваш email

### Проверка API
Убедитесь, что включен **Google Drive API**:
1. **APIs & Services** → **Library**
2. Найдите "Google Drive API"
3. Нажмите **Enable**

## Устранение неполадок

### Если ошибка повторяется:
1. Проверьте, что изменения в Google Cloud Console сохранились
2. Подождите 5-10 минут для полного применения изменений
3. Очистите кэш браузера
4. Попробуйте в режиме инкогнито

### Если не работает Desktop application:
1. Создайте новые credentials для **Web application**
2. Добавьте redirect URI: `http://localhost:8080`
3. Обновите `credentials.json` с новыми данными

## Контакты
Если проблема не решается, проверьте:
- Правильность Client ID и Client Secret
- Включен ли Google Drive API
- Настроен ли OAuth consent screen
- Добавлены ли тестовые пользователи
