# Running AlphaFold inference using Cloud Life Sciences API


```
PROVIDER=google-cls-v2
SEQUENCE=gs://jk-alphafold-datasets/fasta_paths/T1050.fasta
PROJECT=jk-mlops-dev
REGION=us-central1
OUTPUT_PATH=gs://jk-dsub-staging/outputs
REFERENCE_DISK_IMAGE="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000"

dsub 
--provider $PROVIDER \
--project $PROJECT \
--regions $REGION \
--logging $OUTPUT_PATH \
--env \ 
--env \
--env \
--env \
--script run_alphafold_inference.sh
```