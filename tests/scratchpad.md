# Jackhmmer

docker run -it --rm \
-v /mnt/disks/alphafold-datasets:/data \
-v /home/jupyter/alphafold-inference-pipeline/fasta:/fasta \
-v /home/jupyter/alphafold-inference-pipeline:/src \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold-inference


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

# HHblits

python hhblits_runner.py \
--fasta_path /fasta/T1050.fasta \
--database_paths /data/uniclust30/uniclust30_2018_08/uniclust30_2018_08,/data/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
--output_dir /data/output_msas

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
--command 'python /scripts/hhblits_runner.py  --fasta_path ${FASTA_PATH} --output_dir $OUTPUT_PATH --database_paths ${DB}/uniclust30/uniclust30_2018_08/uniclust30_2018_08,${DB}/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt' \
--wait
