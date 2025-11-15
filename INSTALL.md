# Установка на сервер

## Решение проблемы с правами Docker

Если вы видите ошибку `permission denied while trying to connect to the Docker daemon socket`, есть два решения:

### Решение 1: Добавить пользователя в группу docker (рекомендуется)

```bash
# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Применить изменения группы без перелогина
newgrp docker

# Или перелогиниться
exit
# затем ssh снова на сервер

# Проверить что работает
docker ps
```

После этого можно использовать Docker без sudo:
```bash
./docker-run.sh start
```

### Решение 2: Использовать sudo (временное решение)

Измените команды в скрипте на использование sudo:

```bash
# Вместо ./docker-run.sh используйте:
sudo docker compose up -d
sudo docker compose logs -f
sudo docker compose down
```

Или отредактируйте `docker-run.sh`, добавив `sudo` перед каждой командой docker.

## Пошаговая установка на свежий сервер Ubuntu

### 1. Обновите систему

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Установите Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений
newgrp docker

# Включение автозапуска Docker
sudo systemctl enable docker
sudo systemctl start docker

# Проверка установки
docker --version
```

### 3. Установите Git (если не установлен)

```bash
sudo apt install git -y
```

### 4. Клонируйте репозиторий

```bash
cd ~
git clone https://github.com/your-username/card-balance-bot.git
cd card-balance-bot
```

### 5. Настройте переменные окружения

```bash
# Создайте .env из шаблона
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

В .env файле укажите:
- `BOT_TOKEN` - ваш токен от @BotFather
- `API_TRACE_ID` - ваш DNB API trace ID
- Остальные параметры можно оставить по умолчанию

Сохраните файл: `Ctrl+X`, затем `Y`, затем `Enter`

### 6. Сделайте скрипт исполняемым

```bash
chmod +x docker-run.sh
```

### 7. Запустите бота

```bash
./docker-run.sh start
```

### 8. Проверьте что бот работает

```bash
# Просмотр логов
./docker-run.sh logs

# Статус контейнера
./docker-run.sh status

# Использование ресурсов
./docker-run.sh stats
```

Нажмите `Ctrl+C` чтобы выйти из просмотра логов.

## Проверка что бот работает

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте команду `/start`
4. Бот должен ответить приветствием

## Обновление бота

Когда вы обновите код на GitHub:

```bash
cd ~/card-balance-bot

# Получить последние изменения
git pull

# Пересобрать и перезапустить
./docker-run.sh rebuild
```

## Полезные команды

```bash
# Остановка бота
./docker-run.sh stop

# Запуск бота
./docker-run.sh start

# Перезапуск бота
./docker-run.sh restart

# Просмотр логов
./docker-run.sh logs

# Статус
./docker-run.sh status

# Использование CPU/RAM
./docker-run.sh stats
```

## Автоматический перезапуск при загрузке сервера

Docker уже настроен на автозапуск, а контейнер имеет политику `restart: unless-stopped`.

Проверьте что Docker запускается автоматически:
```bash
sudo systemctl is-enabled docker
```

Если вывод `enabled` - всё настроено правильно.

## Резервное копирование

Настройте автоматическое резервное копирование базы данных:

```bash
# Создайте директорию для бэкапов
mkdir -p ~/backups

# Добавьте в crontab
crontab -e

# Добавьте эту строку (бэкап каждый день в 3:00)
0 3 * * * cp ~/card-balance-bot/cards_db.json ~/backups/cards_db_$(date +\%Y\%m\%d).json

# Удаление старых бэкапов (старше 30 дней)
0 4 * * * find ~/backups -name "cards_db_*.json" -mtime +30 -delete
```

## Мониторинг

Добавьте проверку что бот работает:

```bash
crontab -e

# Добавьте эту строку (проверка каждые 5 минут)
*/5 * * * * docker ps | grep dnb-balance-bot > /dev/null || (cd ~/card-balance-bot && ./docker-run.sh start)
```

## Устранение проблем

### Бот не запускается

```bash
# Проверьте логи
./docker-run.sh logs

# Проверьте .env файл
cat .env

# Проверьте что Docker работает
docker ps

# Пересоздайте контейнер
./docker-run.sh rebuild
```

### Порт занят

Бот не использует порты, поэтому эта проблема не должна возникать.

### Нехватка памяти

```bash
# Проверьте использование
./docker-run.sh stats

# Проверьте свободную память на сервере
free -h

# При необходимости уменьшите лимиты в docker-compose.yml
nano docker-compose.yml
# Измените memory: 256M на memory: 128M
# Перезапустите
./docker-run.sh restart
```

### База данных повреждена

```bash
./docker-run.sh stop
cp ~/backups/cards_db_YYYYMMDD.json ~/card-balance-bot/cards_db.json
./docker-run.sh start
```

## Безопасность

1. **Firewall**: Убедитесь что открыт только SSH порт (22)
   ```bash
   sudo ufw status
   sudo ufw allow 22
   sudo ufw enable
   ```

2. **Обновления**: Регулярно обновляйте систему
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **SSH ключи**: Используйте SSH ключи вместо паролей

4. **Не давайте доступ к .env**: В нём хранятся токены

## Логи

Логи автоматически ротируются (максимум 30MB).

Просмотр логов разными способами:
```bash
# Последние 100 строк
docker compose logs --tail=100 bot

# За последний час
docker compose logs --since 1h bot

# Поиск ошибок
docker compose logs bot | grep -i error

# Непрерывный просмотр
./docker-run.sh logs
```

## Контакты для поддержки

При возникновении проблем:
1. Проверьте логи: `./docker-run.sh logs`
2. Создайте issue на GitHub
3. Приложите вывод команд:
   - `docker --version`
   - `./docker-run.sh status`
   - Последние 50 строк логов
