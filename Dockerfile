# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Выполняем миграции и собираем статические файлы (если нужно)
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Команда запуска сервера (можно заменить на gunicorn или другой WSGI сервер)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
