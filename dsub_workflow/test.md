

./run_alphafold_inference.sh \
-p jk-mlops-dev \
-l us-central1 \
-f gs://jk-alphafold-datasets/fasta_paths/T1050.fasta \
-o gs://jk-dsub-staging/outputs \
-d "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000" 

