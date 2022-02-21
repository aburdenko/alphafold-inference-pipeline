
```

./run_alphafold_inference.sh \
-p jk-mlops-dev \
-l us-central1 \
-f gs://jk-alphafold-datasets/fasta_paths/T1050.fasta \
-o gs://jk-dsub-staging/outputs \
-d "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000"

```

```
export SEQUENCE=gs://jk-alphafold-datasets/fasta_paths/T1050.fasta
export MAX_TEMPLATE_DATE=2020-05-14
export PROJECT=jk-mlops-dev
export REGION=us-central1
export OUTPUT_PATH=gs://jk-dsub-staging/outputs
export REFERENCE_DISK="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000"
export MODEL_PARAMS=gs://jk-alphafold-datasets-archive/jan-22/params


./run_alphafold_inference.sh

```


