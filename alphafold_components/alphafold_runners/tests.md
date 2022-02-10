
### Testing jackhmmer runner

```
docker run -it --rm --entrypoint /bin/bash \
-v /mnt/disks/alphafold-datasets:/data \
-v /home/jupyter/alphafold-inference-pipeline:/src \
-v /home/jupyter/output:/output \
gcr.io/jk-mlops-dev/alphafold
```


```
export PYTHONPATH=/app/alphafold
export FASTA_PATH=/src/fasta/T1050.fasta
export OUTPUT_DIR=/output/msas
export DATABASES_ROOT=/data 
export DATABASE_PATHS=uniref90/uniref90.fasta
export N_CPU=4
export MAX_STO_SEQUENCES=500
export MSA_TOOL=jackhmmer

python msa_runner.py
```



### Testing hhblits runner





```
export PYTHONPATH=/app/alphafold
export FASTA_PATH=/src/fasta/T1050.fasta
export OUTPUT_DIR=/output/msas
export DATABASE_PATHS=/data/uniclust30/uniclust30_2018_08/uniclust30_2018_08,/data/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt
export N_CPU=4
export MSA_TOOL=hhblits

python msa_runner.py
```



### Testing hhsearch runner





```
export PYTHONPATH=/app/alphafold
export MSA_PATH=/output/msas/OUTPUT.sto
export OUTPUT_DIR=/output/msas 
export DATABASE_PATHS=/data/pdb70/pdb70 
export MAXSEQ=1_000_000
export TEMPLATE_TOOL=hhsearch

python template_runner.py
```