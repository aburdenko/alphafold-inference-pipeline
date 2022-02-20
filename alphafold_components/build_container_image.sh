#!/usr/bin/env bash
set -e

PROJECT=${1:-jk-mlops-dev}
TAG=${2:-latest}
IMAGE_NAME=gcr.io/${PROJECT}/alphafold-components:${TAG}

docker build -t ${IMAGE_NAME} -f Dockerfile .
docker push ${IMAGE_NAME}
