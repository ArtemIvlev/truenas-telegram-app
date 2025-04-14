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

# Включаем BuildKit для ускорения сборки
export DOCKER_BUILDKIT=1

echo "Сборка Docker образа..."
docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest \
    --target builder \
    --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:builder \
    --progress=plain \
    .

docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:builder \
    --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP} \
    --tag ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest \
    --progress=plain \
    .

echo "Публикация в Docker Hub..."
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest
docker push ${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:builder

echo "Готово! Образ опубликован как:"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:${TIMESTAMP}"
echo "${DOCKERHUB_USERNAME}/${REPOSITORY_NAME}:latest" 