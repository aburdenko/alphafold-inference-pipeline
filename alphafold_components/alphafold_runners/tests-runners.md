docker run -it --rm \
-v /mnt:/data \
-v /home/jupyter/features:/features \
-v /home/jupyter/alphafold-inference-pipeline:/scripts \
-v /home/jupyter/alphafold-inference-pipeline/sequences/:/sequences \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold


## jackhmmer

export INPUT_PATH=/sequences/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export DB_ROOT=/data/disks/alphafold
export DB_PATH=uniref90/uniref90.fasta
export N_CPU=8
export MAXSEQ=10_000

python /scripts/alphafold_components/alphafold_runners/jackhmmer_runner.py


## HHblits

export INPUT_PATH=/sequences/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export N_CPU=8
export MAXSEQ=1_000_000
export DB_ROOT=/data/disks/alphafold
export DB_PATHS=bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt

python /scripts/alphafold_components/alphafold_runners/hhblits_runner.py

export INPUT_PATH=/fasta/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export N_CPU=8
export MAXSEQ=1_000_000
export DB_ROOT=/data
export DB_PATHS=/data/uniclust30/uniclust30_2018_08/uniclust30_2018_08

python /scripts/alphafold_components/alphafold_runners/hhblits_runner.py


## predict relax

docker run -it --rm --gpus all \
-v /mnt:/data \
-v /home/jupyter/features:/features \
-v /home/jupyter/alphafold-inference-pipeline:/scripts \
-v /home/jupyter/alphafold-inference-pipeline/sequences/:/sequences \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold

export DB_ROOT=/data
export PARAMS_PATH=params
export FEATURES_PATH=features/features.pkl
export MODEL_NAME=model_1
export NUM_ENSEMBLE=1
export OUTPUT_DIR=/output/testing/predict

python /scripts/alphafold_components/alphafold_runners/predict_runner.py



