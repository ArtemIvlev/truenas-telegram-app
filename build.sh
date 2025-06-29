#!/bin/bash

# Проверяем наличие аргументов
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Использование: $0 <dockerhub_username> <repository_name> [use_cache]"
    echo "  use_cache: true/false (по умолчанию: true)"
    exit 1
fi

DOCKERHUB_USERNAME=$1
REPOSITORY_NAME=$2
USE_CACHE=${3:-true}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Обновляем подмодуль
echo "Обновление подмодуля..."
git submodule update --init --recursive
git submodule update --remote

# Отключаем BuildKit
export DOCKER_BUILDKIT=0

echo "Сборка Docker образа..."
# Сборка образа с учетом параметра кеша
if [ "$USE_CACHE" = "false" ]; then
    echo "Сборка без использования кеша..."
    docker build \
        --no-cache \
        --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP} \
        --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest \
        --build-arg VERSION=${TIMESTAMP} \
        --build-arg BUILD_CACHE=false \
        .
else
    echo "Сборка с использованием кеша..."
    docker build \
        --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP} \
        --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest \
        --build-arg VERSION=${TIMESTAMP} \
        --build-arg BUILD_CACHE=true \
        .
fi

echo "Публикация в Docker Hub..."
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest

echo "Готово! Образ опубликован как:"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest" 