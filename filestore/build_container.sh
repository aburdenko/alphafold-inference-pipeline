IMAGE_NAME=${1:-gcr.io/jk-mlops-dev/nfs-test}

docker build -t ${IMAGE_NAME} -f Dockerfile .
docker push ${IMAGE_NAME}