
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
export INPUT_DATA=/src/fasta/T1050.fasta
export INPUT_DATA_FORMAT=fasta 
export OUTPUT_DATA=/output/testing/jackhmmer/output.sto
export OUTPUT_DATA_FORMAT=sto 
export DB_ROOT=/data 
export DB_PATHS=uniref90/uniref90.fasta 
export N_CPU=4 
export MAXSEQ=10_000 
export DB_TOOL=jackhmmer

python db_search_runner.py
```



### Testing hhblits runner



```
export PYTHONPATH=/app/alphafold
export INPUT_DATA=/src/fasta/T1050.fasta
export INPUT_DATA_FORMAT=fasta
export OUTPUT_DATA=/output/testing/hhblits/output.a3m
export OUTPUT_DATA_FORMAT=a3m
export DB_ROOT=/data
export DB_PATHS=uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt
export N_CPU=8
export MAXSEQ=1_000_000
export DB_TOOL=hhblits

python db_search_runner.py
```



### Testing hhsearch runner



```
export PYTHONPATH=/app/alphafold
export INPUT_SEQUENCE_PATH=/src/fasta/T1050.fasta
export INPUT_MSA_PATH=/output/msas/uniref90_results.sto
export MSA_DATA_FORMAT=sto
export OUTPUT_TEMPLATE_HITS_PATH=/output/testing/hhsearch/output.hhr
export OUTPUT_TEMPLATE_FEATURES_PATH=/output/testing/hhsearch/template_features.pkl
export MAX_TEMPLATE_DATE=2020-05-14
export DB_ROOT=/data 
export DB_PATHS=pdb70/pdb70 
export MAXSEQ=1_000_000
export MMCIF_PATH=pdb_mmcif/mmcif_files
export OBSOLETE_PATH=pdb_mmcif/obsolete.dat

python hhsearch_runner.py
```