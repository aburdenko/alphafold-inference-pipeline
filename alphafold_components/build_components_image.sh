#!/usr/bin/env bash
set -e

PROJECT=${1:-jk-mlops-dev}
TAG=${2:-latest}
IMAGE_NAME=gcr.io/${PROJECT}/alphafold:${TAG}

docker build --tag ${IMAGE_NAME} -f Dockerfile.alphafold_runners .
docker push ${IMAGE_NAME}

