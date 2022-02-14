#!/usr/bin/env bash
set -e

PROJECT=${1:-jk-mlops-dev}
TAG=${2:-latest}
IMAGE_NAME=gcr.io/${PROJECT}/alphafold:${TAG}

git clone https://github.com/deepmind/alphafold.git
cp Dockerfile.alphafold alphafold/docker/Dockerfile
cd alphafold && docker build --tag ${IMAGE_NAME} -f docker/Dockerfile .
docker push ${IMAGE_NAME}

cd ..
rm -fr alphafold
