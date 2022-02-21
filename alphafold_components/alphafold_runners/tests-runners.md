docker run -it --rm \
-v /mnt:/data \
-v /home/jupyter/testing:/inputs \
-v /home/jupyter/alphafold-inference-pipeline:/src \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold-components



## jackhmmer


export INPUT_PATH=/sequences/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export DB_ROOT=/data/disks/alphafold
export DB_PATH=uniref90/uniref90.fasta
export N_CPU=8
export MAXSEQ=10_000

python /src/alphafold_components/alphafold_runners/jackhmmer_runner.py


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


## aggregate features

export SEQUENCE_PATH=/src/sequences/T1050.fasta
export MSAS_PATH=/inputs/msas
export TEMPLATE_FEATURES_PATH=/inputs/templates/pdb/features.pkl
export OUTPUT_FEATURES_PATH=/output/testing/aggregate/features.pkl

python /src/alphafold_components/alphafold_runners/aggregate_features_runner.py



## Predict 

docker run -it --rm --gpus all \
-v /home/jupyter/testing:/inputs \
-v /home/jupyter/alphafold-inference-pipeline:/src \
-v /home/jupyter/output:/output \
-e PYTHONPATH=/app/alphafold \
--entrypoint /bin/bash \
gcr.io/jk-mlops-dev/alphafold-components



export MODEL_PARAMS_PATH=/inputs/params
export FEATURES_PATH=/inputs/features/features.pkl
export MODEL_NAME=model_1
export NUM_ENSEMBLE=1
export RANDOM_SEED=0
export RAW_PREDICTION_PATH=/output/testing/predict/prediction.pkl
export UNRELAXED_PROTEIN_PATH=/output/testing/predict/unrelaxed_protein.pdb

python /src/alphafold_components/alphafold_runners/predict_runner.py

## Relax

export UNRELAXED_PROTEIN_PATH=/inputs/unrelaxed_proteins/unrelaxed_protein.pdb
export RELAXED_PROTEIN_PATH=/output/testing/relax/relaxed_protein.pdb
export RELAX_USE_GPU=1

python /src/alphafold_components/alphafold_runners/relax_runner.py


### Relax predict

export MODEL_PARAMS_PATH=/inputs/params
export FEATURES_PATH=/inputs/features/features.pkl
export MODEL_NAME=model_1
export NUM_ENSEMBLE=1
export RANDOM_SEED=0
export RAW_PREDICTION_PATH=/output/testing/predict/prediction.pkl
export UNRELAXED_PROTEIN_PATH=/output/testing/predict/unrelaxed_protein.pdb
export RELAXED_PROTEIN_PATH=/output/testing/relax/relaxed_protein.pdb
export RELAX_USE_GPU=1

python /src/alphafold_components/alphafold_runners/predict_relax_runner.py



