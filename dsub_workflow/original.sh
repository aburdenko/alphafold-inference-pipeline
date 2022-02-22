#!/bin/bash
# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is a simple wrapper on top of dsub. In this "incarnation"
# we use dsub --wait option to wait for the CLS pipeline to complete
# The next step would be to retrieve status and logs on a more regular
# basis so we can push it back to Vertex Pipelines

cd /app/alphafold

echo "Starting pipeline on $(date)"
pipeline_start_time=$(date +%s)

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
 --model_preset=monomer \
 --max_template_date=2020-05-14 \
 --db_preset=full_dbs \
 --benchmark=False \
 --logtostderr \
 --use_gpu_relax

pipeline_end_time=$(date +%s)
echo "Pipeline completed on: $(date)"
echo "Pipeline elapsed time $(( $pipeline_end_time - $pipeline_start_time ))"
