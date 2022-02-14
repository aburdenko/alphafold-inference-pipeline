CLS_WRAPPERS_IMAGE_NAME=${1:-gcr.io/jk-mlops-dev/cls-wrappers}

docker build -t ${CLS_WRAPPERS_IMAGE_NAME} -f Dockerfile.cls_wrappers .
docker push ${CLS_WRAPPERS_IMAGE_NAME}
