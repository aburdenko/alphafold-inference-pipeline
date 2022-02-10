IMAGE_NAME=${1:-gcr.io/jk-mlops-dev/alphafold-components}

docker build -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}