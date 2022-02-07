python jackhmmer_runner.py \
--fasta_path /fasta/T1050.fasta \
--database_path /data/uniref90/uniref90.fasta \
--n_cpu 8 \
--max_sto_sequences 501 \
--output_dir /data/output_msas



dsub --provider google-cls-v2 \
--image gcr.io/jk-mlops-dev/alphafold-inference \
--boot-disk-size 100 \
--mount DB="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000" \
--machine-type n1-standard-8 \
--project jk-mlops-dev \
--regions us-central1 \
--logging gs://jk-dsub-staging/logging/ \
--command 'ls -la $DB' \
--wait


dsub --provider google-cls-v2 \
--image gcr.io/jk-mlops-dev/alphafold-inference \
--boot-disk-size 100 \
--mount DB="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000" \
--machine-type n1-standard-8 \
--project jk-mlops-dev \
--regions us-central1 \
--logging gs://jk-dsub-staging/logging/ \
--input FASTA_PATH=gs://jk-alphafold-datasets/fasta_paths/T1050.fasta \
--output-recursive OUTPUT_PATH=gs://jk-dsub-staging/output \
--command 'python /scripts/jackhmmer_runner.py  --fasta_path ${FASTA_PATH} --output_dir $OUTPUT_PATH --database_path ${DB}/uniref90/uniref90.fasta' \
--wait


dsub --provider google-cls-v2 \
--image gcr.io/jk-mlops-dev/alphafold-inference \
--boot-disk-size 100 \
--machine-type n1-standard-8 \
--project jk-mlops-dev \
--regions us-west1 \
--logging gs://jk-dsub-staging/logging/ \
--output OUT=gs://jk-dsub-staging/out/out.txt \
--command 'ls -la ${DB}' \
--wait