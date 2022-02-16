
```
export TARGET=T1061
export EXPERIMENT_NAME=${TARGET}-$(date +"%Y-%m-%d-%M-%s")
export STAGING_BUCKET=gs://jk-alphafold-staging
export MACHINE_TYPE=a2-highgpu-1g
export GPU_TYPE=nvidia-tesla-a100
export GPU_COUNT=1
export PROJECT=jk-mlops-dev
export REGION=us-central1
export IMAGE=gcr.io/jk-mlops-dev/alphafold
export DISK_IMAGE="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000"
export OUTPUT_PATH=${STAGING_BUCKET}/perf_tests/${EXPERIMENT_NAME}/output
export LOGGING=${STAGING_BUCKET}/perf_tests/${EXPERIMENT_NAME}/logging

dsub --provider google-cls-v2 \
--script alphafold.sh \
--project $PROJECT \
--regions $REGION \
--image $IMAGE \
--boot-disk-size 100 \
--mount DB="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000" \
--machine-type ${MACHINE_TYPE} \
--accelerator-type ${GPU_TYPE} \
--accelerator-count ${GPU_COUNT} \
--logging $LOGGING \
--input FASTA=${STAGING_BUCKET}/fasta/${TARGET}.fasta \
--output-recursive $OUTPUT_PATH \
--env TF_FORCE_UNIFIED_MEMORY=1 \
--env XLA_PYTHON_CLIENT_MEM_FRACTION=2.0 \
--wait


