# 🚀 Weather Forecast Application

## 📋 Предварительные требования
1. Установите [Docker](https://docs.docker.com/get-docker/)
2. Установите [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Быстрый старт
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/podlizka-2/weather_forecast.git 

   cd weather-forecast
   ```
2. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build
   ```
3. Приложение будет доступно по адресу:  
   http://localhost:8000

## ⚙️ Конфигурация
Создайте файл `.env` в корне проекта:
```env
# Django
DEBUG=1
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0

# API Keys
OPENCAGE_API_KEY=your_opencage_api_key_here
```

Пример Dockerfile:
```Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🛠 Команды управления
| Команда | Описание |
|---------|----------|
| `docker-compose up` | Запуск контейнеров |
| `docker-compose down` | Остановка контейнеров |
| `docker-compose logs -f` | Просмотр логов в реальном времени |
| `docker-compose exec web bash` | Доступ к контейнеру |

## 🔧 Устранение неполадок
Если возникают ошибки зависимостей:
```bash
docker-compose build --no-cache
```

Для применения миграций:
```bash
docker-compose exec web python manage.py migrate
```

## 🌐 Доступ к приложению
- Основное приложение: http://localhost:8000
- Админ-панель: http://localhost:8000/admin (создайте суперпользователя командой `docker-compose exec web python manage.py createsuperuser`)

