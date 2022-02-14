CLS_WRAPPERS_IMAGE_NAME=${1:-gcr.io/jk-mlops-dev/cls-wrappers}
ALPHAFOLD_COMPONENTS_IMAGE_NAME=${2:-gcr.io/jk-mlops-dev/alphafold-components}

docker build -t ${CLS_WRAPPERS_IMAGE_NAME} -f Dockerfile.cls_wrappers .
docker push ${CLS_WRAPPERS_IMAGE_NAME}

docker build -t ${ALPHAFOLD_COMPONENTS_IMAGE_NAME} -f Dockerfile.alphafold_components .
docker push ${ALPHAFOLD_COMPONENTS_IMAGE_NAME}