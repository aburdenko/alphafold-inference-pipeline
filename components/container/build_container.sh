IMAGE_NAME=${1:-gcr.io/jk-mlops-dev/dsub}

docker build -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}