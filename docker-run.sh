#!/bin/bash

# Скрипт для управления Docker контейнером бота

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода цветного текста
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия .env файла
check_env_file() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Creating .env from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your actual credentials before starting the bot"
            exit 1
        else
            print_error ".env.example not found!"
            exit 1
        fi
    fi
}

# Запуск контейнера
start() {
    print_info "Starting DNB Balance Bot..."
    check_env_file
    docker compose up -d
    print_info "Bot started successfully!"
    print_info "Use './docker-run.sh logs' to view logs"
}

# Остановка контейнера
stop() {
    print_info "Stopping DNB Balance Bot..."
    docker compose down
    print_info "Bot stopped successfully!"
}

# Перезапуск контейнера
restart() {
    print_info "Restarting DNB Balance Bot..."
    docker compose restart
    print_info "Bot restarted successfully!"
}

# Просмотр логов
logs() {
    docker compose logs -f bot
}

# Пересборка образа
rebuild() {
    print_info "Rebuilding Docker image..."
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    print_info "Bot rebuilt and started successfully!"
}

# Статус контейнера
status() {
    docker compose ps
}

# Просмотр использования ресурсов
stats() {
    docker stats dnb-balance-bot
}

# Очистка (остановка и удаление контейнера и образа)
clean() {
    print_warning "This will stop and remove the container and image. Database will be preserved."
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker compose down --rmi all
        print_info "Cleanup completed!"
    else
        print_info "Cleanup cancelled"
    fi
}

# Помощь
help() {
    echo "DNB Balance Bot - Docker Management Script"
    echo ""
    echo "Usage: ./docker-run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start    - Start the bot container"
    echo "  stop     - Stop the bot container"
    echo "  restart  - Restart the bot container"
    echo "  logs     - View bot logs (follow mode)"
    echo "  rebuild  - Rebuild Docker image and restart"
    echo "  status   - Show container status"
    echo "  stats    - Show resource usage"
    echo "  clean    - Stop and remove container and image"
    echo "  help     - Show this help message"
    echo ""
}

# Обработка команд
case "${1}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    rebuild)
        rebuild
        ;;
    status)
        status
        ;;
    stats)
        stats
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: ${1}"
        echo ""
        help
        exit 1
        ;;
esac
