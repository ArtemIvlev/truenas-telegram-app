#!/bin/bash

# Проверка наличия аргументов
if [ "$#" -ne 2 ]; then
    echo "Использование: $0 <dockerhub_username> <image_name>"
    echo "Пример: $0 myusername nude-detection-service"
    exit 1
fi

DOCKERHUB_USERNAME=$1
IMAGE_NAME=$2
VERSION=$(date +%Y%m%d_%H%M%S)

# Сборка образа
echo "Сборка Docker образа..."
docker build -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION} .
docker tag ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION} ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

# Публикация в Docker Hub
echo "Публикация в Docker Hub..."
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

echo "Готово! Образ опубликован как:"
echo "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo "${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest" 