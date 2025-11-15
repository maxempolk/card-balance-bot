# Используем легковесный Alpine образ Python
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения для оптимизации Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Копируем только requirements.txt сначала для кеширования слоя
COPY requirements.txt .

# Устанавливаем зависимости
# Используем --no-cache-dir для экономии места
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY main.py .
COPY database.py .
COPY api_client.py .
COPY config.py .
COPY messages.py .
COPY payment_checker.py .
COPY .env .

# Создаем непривилегированного пользователя для безопасности
RUN adduser -D -u 1000 botuser && \
    chown -R botuser:botuser /app

# Переключаемся на непривилегированного пользователя
USER botuser

# Запускаем бота
CMD ["python", "-u", "main.py"]
