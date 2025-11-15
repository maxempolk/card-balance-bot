# Docker Deployment Guide

## Преимущества Docker для слабых серверов

✅ Изолированная среда
✅ Ограничение использования ресурсов (CPU/RAM)
✅ Автоматический перезапуск при сбоях
✅ Легкое обновление и откат версий
✅ Компактный Alpine образ (~150MB)

## Быстрый старт

### 1. Убедитесь что Docker установлен

```bash
docker --version
docker-compose --version
```

Если Docker не установлен:
```bash
# Для Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Для других систем см. https://docs.docker.com/get-docker/
```

### 2. Настройте .env файл

```bash
cp .env.example .env
nano .env  # или vim .env
```

### 3. Запустите бота

```bash
# С использованием скрипта (рекомендуется)
chmod +x docker-run.sh
./docker-run.sh start

# Или напрямую через docker-compose
docker-compose up -d
```

## Управление через docker-run.sh

Скрипт `docker-run.sh` предоставляет удобные команды:

```bash
# Запуск бота
./docker-run.sh start

# Остановка бота
./docker-run.sh stop

# Перезапуск бота
./docker-run.sh restart

# Просмотр логов (с автообновлением)
./docker-run.sh logs

# Пересборка образа (после изменения кода)
./docker-run.sh rebuild

# Статус контейнера
./docker-run.sh status

# Использование ресурсов (CPU, RAM)
./docker-run.sh stats

# Полная очистка (удаление контейнера и образа)
./docker-run.sh clean

# Справка
./docker-run.sh help
```

## Ограничения ресурсов

Настроены в `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'      # Максимум 50% одного ядра CPU
      memory: 256M     # Максимум 256MB RAM
    reservations:
      cpus: '0.1'      # Минимум 10% одного ядра CPU
      memory: 64M      # Минимум 64MB RAM
```

### Настройка под ваш сервер

Отредактируйте `docker-compose.yml` если нужно изменить лимиты:

**Для очень слабого сервера** (512MB RAM):
```yaml
limits:
  cpus: '0.3'
  memory: 128M
reservations:
  cpus: '0.05'
  memory: 32M
```

**Для мощного сервера**:
```yaml
limits:
  cpus: '1.0'
  memory: 512M
reservations:
  cpus: '0.2'
  memory: 128M
```

## Логирование

Логи ограничены для экономии места:
- Максимальный размер файла: 10MB
- Количество файлов: 3 (всего 30MB)

Просмотр логов:
```bash
# С автообновлением
./docker-run.sh logs

# Последние 100 строк
docker-compose logs --tail=100 bot

# Логи за последний час
docker-compose logs --since 1h bot
```

## Резервное копирование базы данных

База данных автоматически сохраняется на хосте:

```bash
# Создание бэкапа
cp cards_db.json cards_db.json.backup

# Восстановление из бэкапа
cp cards_db.json.backup cards_db.json
docker-compose restart
```

## Обновление бота

### Способ 1: С сохранением данных

```bash
git pull
./docker-run.sh rebuild
```

### Способ 2: Ручное обновление

```bash
# Остановка
docker-compose down

# Обновление кода
git pull

# Пересборка образа
docker-compose build --no-cache

# Запуск
docker-compose up -d
```

## Мониторинг

### Проверка статуса

```bash
./docker-run.sh status
```

### Использование ресурсов в реальном времени

```bash
./docker-run.sh stats
```

### Проверка здоровья бота

```bash
# Проверить что контейнер работает
docker ps | grep dnb-balance-bot

# Проверить логи на ошибки
docker-compose logs --tail=50 bot | grep -i error
```

## Автозапуск при перезагрузке сервера

Контейнер настроен на автоматический запуск (`restart: unless-stopped`).

Для гарантированного запуска Docker при загрузке системы:

```bash
sudo systemctl enable docker
```

## Полезные команды Docker

```bash
# Список всех контейнеров
docker ps -a

# Использование места на диске
docker system df

# Очистка неиспользуемых образов и контейнеров
docker system prune -a

# Просмотр логов конкретного контейнера
docker logs dnb-balance-bot

# Выполнение команды внутри контейнера
docker exec -it dnb-balance-bot sh

# Копирование файла из контейнера
docker cp dnb-balance-bot:/app/cards_db.json ./backup.json
```

## Устранение проблем

### Бот не запускается

```bash
# Проверьте логи
./docker-run.sh logs

# Проверьте .env файл
cat .env

# Пересоздайте контейнер
./docker-run.sh rebuild
```

### Нехватка памяти

```bash
# Проверьте использование памяти
./docker-run.sh stats

# Уменьшите лимиты в docker-compose.yml
# Перезапустите
./docker-run.sh restart
```

### База данных повреждена

```bash
# Остановите бота
./docker-run.sh stop

# Восстановите из бэкапа
cp cards_db.json.backup cards_db.json

# Запустите
./docker-run.sh start
```

## Безопасность

1. **Не публикуйте порты наружу** - бот работает только с Telegram API
2. **Храните .env в секрете** - добавлен в .gitignore
3. **Регулярно обновляйте образ**:
   ```bash
   docker pull python:3.11-alpine
   ./docker-run.sh rebuild
   ```
4. **Используйте непривилегированного пользователя** - уже настроено в Dockerfile

## Production советы

1. **Настройте автоматические бэкапы**:
   ```bash
   # Добавьте в crontab
   0 3 * * * cp /path/to/cards_db.json /path/to/backup/cards_db.json.$(date +\%Y\%m\%d)
   ```

2. **Мониторинг работоспособности**:
   ```bash
   # Проверка каждые 5 минут
   */5 * * * * docker ps | grep dnb-balance-bot || docker-compose up -d
   ```

3. **Логирование через syslog** (опционально):
   Измените в docker-compose.yml:
   ```yaml
   logging:
     driver: "syslog"
     options:
       tag: "dnb-bot"
   ```

4. **Используйте Docker Swarm** для высокой доступности (advanced):
   ```bash
   docker stack deploy -c docker-compose.yml dnb-bot
   ```
