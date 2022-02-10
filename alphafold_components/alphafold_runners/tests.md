
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
export INPUT_PATH=/src/fasta/T1050.fasta
export OUTPUT_PATH=/output/testing/jackhmmer/output.sto
export DATABASES_ROOT=/data 
export DATABASE_PATHS=uniref90/uniref90.fasta
export N_CPU=4
export MAX_STO_SEQUENCES=10000
export DB_TOOL=jackhmmer

python db_search_runner.py
```



### Testing hhblits runner



```
export PYTHONPATH=/app/alphafold
export INPUT_PATH=/src/fasta/T1050.fasta
export OUTPUT_PATH=/output/testing/hhblits/output.a3m
export DATABASES_ROOT=/data
export DATABASE_PATHS=uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt
export N_CPU=8
export DB_TOOL=hhblits

python db_search_runner.py
```



### Testing hhsearch runner



```
export PYTHONPATH=/app/alphafold
export INPUT_PATH=/output/msas/uniref90_results.sto
export OUTPUT_PATH=/output/testing/hhsearch/output.hhr
export DATABASES_ROOT=/data 
export DATABASE_PATHS=pdb70/pdb70 
export MAXSEQ=1_000_000
export DB_TOOL=hhsearch

python db_search_runner.py
```