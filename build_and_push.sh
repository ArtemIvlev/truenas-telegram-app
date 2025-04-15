#!/bin/bash

# Проверяем наличие аргументов
if [ "$#" -ne 2 ]; then
    echo "Использование: $0 <dockerhub_username> <repository_name>"
    exit 1
fi

DOCKERHUB_USERNAME=$1
REPOSITORY_NAME=$2
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Обновляем подмодуль
echo "Обновление подмодуля..."
git submodule update --init --recursive
git submodule update --remote

# Отключаем BuildKit
export DOCKER_BUILDKIT=0

echo "Сборка Docker образа..."
# Полная пересборка образа без кеша
docker build \
    --no-cache \
    --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP} \
    --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest \
    --build-arg VERSION=${TIMESTAMP} \
    .

echo "Публикация в Docker Hub..."
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest

echo "Готово! Образ опубликован как:"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest" 