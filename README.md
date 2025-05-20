# School Testing Application

Это веб-приложение для тестирования учеников.

## Стек технологий

### Frontend
- React 19.1.0
- React Router DOM
- TypeScript

### Backend
- Python
- (Укажите версию Python и основные библиотеки)

## Установка и запуск

### Frontend
```bash
# Установка зависимостей
npm install

# Запуск разработки
npm start

# Сборка для продакшена
npm run build
```

### Backend
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python app/main.py
```

## Деплой на Render

1. Создайте аккаунт на Render.com
2. Свяжите ваш GitHub репозиторий с Render
3. Настройте переменные окружения в панели управления Render
4. Запустите деплой фронтенда и бэкенда как отдельные сервисы

## Переменные окружения

Создайте файл `.env` с необходимыми переменными:
```
# Frontend
REACT_APP_API_URL=your-api-url

# Backend
DATABASE_URL=your-database-url
SECRET_KEY=your-secret-key
```
