

start_time_display=$(date)
start_time=$(date +%s)
echo "Starting run_alphafold.py pipeline: $start_time_display"

python /app/alphafold/run_alphafold.py \
 --fasta_paths=${FASTA} \
 --uniref90_database_path=${DB}/uniref90/uniref90.fasta \
 --mgnify_database_path=${DB}/mgnify/mgy_clusters_2018_12.fa \
 --pdb70_database_path=${DB}/pdb70/pdb70 \
 --data_dir=${DB} \
 --template_mmcif_dir=${DB}/pdb_mmcif/mmcif_files \
 --obsolete_pdbs_path=${DB}/pdb_mmcif/obsolete.dat \
 --uniclust30_database_path=${DB}/uniclust30/uniclust30_2018_08/uniclust30_2018_08 \
 --bfd_database_path=${DB}/bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt \
 --output_dir=${OUT_PATH} \
 --max_template_date=2020-05-14 \
 --benchmark=False \
 --use_gpu_relax


end_time_display=$(date)
end_time=$(date +%s)
elapsed=$(( end_time - start_time ))
echo "Pipeline completed: $(date)"
echo "Elapsed time: $elapsed" 