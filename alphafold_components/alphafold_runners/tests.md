docker run -it --rm \
-v /mnt/disks/alphafold-datasets:/data \
-v /home/jupyter/alphafold-inference-pipeline:/scripts \
-v /home/jupyter/alphafold-inference-pipeline/sequences/:/sequences \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold


docker run -it --rm \
-v /mnt/nfs/alphafold:/data \
-v /home/jupyter/alphafold-inference-pipeline:/scripts \
-v /home/jupyter/alphafold-inference-pipeline/sequences/:/sequences \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold



## HHblits

export INPUT_PATH=/fasta/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export N_CPU=8
export MAXSEQ=1_000_000
export DB_ROOT=/data
export DB_PATHS=uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt

python /scripts/alphafold_components/alphafold_runners/hhblits_runner.py


dsub --provider google-cls-v2 \
--image gcr.io/jk-mlops-dev/alphafold \
--boot-disk-size 200 \
--mount DB_ROOT="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000" \
--machine-type c2-standard-8 \
--project jk-mlops-dev \
--regions us-central1 \
--logging gs://jk-dsub-staging/logging/ \
--input INPUT_PATH=gs://jk-alphafold-datasets/fasta_paths/T1050.fasta \
--output OUTPUT_PATH=gs://jk-dsub-staging/output/hhblits/output.a3m \
--script ./alphafold_components/alphafold_runners/hhblits_runner.py \
--env DB_PATHS=uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
--env N_CPU=4 \
--env MAXSEQ=1_000_000 \
--env PYTHONPATH=/app/alphafold \
--wait \
--summary

