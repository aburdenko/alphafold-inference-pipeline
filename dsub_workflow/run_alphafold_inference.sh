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

set -o errexit
set -o nounset

trap 'exit_handler $? $LINENO' 1 2 3 15 ERR  

exit_handler() {
    echo "Error $1 occured in line $2"
    
    # Delete orphaned jobs
    for job_id in "${job_ids[@]}"
    do
        echo "Deleting job $job_id" 
        ddel --provider  "$DSUB_PROVIDER" --project "$PROJECT" --job "$job_id"
    done
}

function usage {
    echo "Usage ..."
    exit 1
}

readonly DSUB_PROVIDER=google-cls-v2
#readonly DSUB_PROVIDER=local
readonly POLLING_INTERVAL=30s
readonly JACKHMMER_MACHINE_TYPE=n1-standard-8
readonly HHBLITS_MACHINE_TYPE=c2-standard-16
readonly HHSEARCH_MACHINE_TYPE=c2-standard-16
readonly AGGREGATE_MACHINE_TYPE=n1-standard-8
readonly PREDICT_MACHINE_TYPE=a2-highgpu-1g
readonly BOOT_DISK_SIZE=200
readonly PREDICT_ACCELERATOR_TYPE=nvidia-tesla-a100
readonly PREDICT_ACCELERATOR_COUNT=1

readonly JACKHMMER_CPU=8
readonly HHBLITS_CPU=12

readonly IMAGE=gcr.io/jk-mlops-dev/alphafold-components
readonly JACKHMMER_COMMAND='python /scripts/alphafold_runners/jackhmmer_runner.py'
readonly HHBLITS_COMMAND='python /scripts/alphafold_runners/hhblits_runner.py'
readonly HHSEARCH_COMMAND='python /scripts/alphafold_runners/hhsearch_runner.py'
readonly AGGREGATE_COMMAND='python /scripts/alphafold_runners/aggregate_features_runner.py'
readonly PREDICT_COMMAND='python /scripts/alphafold_runners/predict_relax_runner.py'

readonly UNIREF90_PATH='uniref90/uniref90.fasta'
readonly MGNIFY_PATH='mgnify/mgy_clusters_2018_12.fa'
readonly BFD_PATH='bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'
readonly UNICLUST30_PATH='uniclust30/uniclust30_2018_08/uniclust30_2018_08'
readonly UNIPROT_PATH='uniprot/uniprot.fasta'
readonly PDB70_PATH='pdb70/pdb70'
readonly PDB_MMCIF_PATH='pdb_mmcif/mmcif_files'
readonly PDB_OBSOLETE_PATH='pdb_mmcif/obsolete.dat'
readonly PDB_SEQRES_PATH='pdb_seqres/pdb_seqres.txt'

readonly UNIREF90_MAXSEQ=10_000
readonly MGNIFY_MAXSEQ=10_000
readonly UNICLUST30_MAXSEQ=1_000_000
readonly BFD_MAXSEQ=1_000_000
readonly PDB_MAXSEQ=1_000_000

readonly RELAX_USE_GPU=1



# Check the input parameters
if [[ -z ${SEQUENCE+x} ]] || \
   [[ -z ${PROJECT+x} ]] || \
   [[ -z ${REGION+x} ]] || \
   [[ -z ${OUTPUT_PATH+x} ]] || \
   [[ -z ${REFERENCE_DISK+x} ]] || \
   [[ -z ${MAX_TEMPLATE_DATE+x} ]] || \
   [[ -z ${MODEL_PARAMS+x} ]]
then
    usage
fi

output_path="${OUTPUT_PATH}/$(date +"%Y-%m-%d-%H-%M-%S")"
output_path=gs://jk-dsub-staging/outputs/2022-02-21-21-28-57
echo "Starting the pipeline on: $(date)"
echo "Pipeline outputs at: ${output_path}"
pipeline_start_time=$(date +%s)
job_ids=()

echo "Starting feature engineering on: $(date)"
feature_engineering_start_time=$(date +%s)

echo "Starting Uniref90 search on: $(date)" 
task=uniref90_search
logging_path="${output_path}/logging/${task}"
uniref_output_msa_path="${output_path}/msas/${task}.sto"
uniref90_job_id=$(dsub \
--skip \
--name "$task" \
--command "$JACKHMMER_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$JACKHMMER_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input INPUT_PATH="$SEQUENCE" \
--output OUTPUT_PATH="$uniref_output_msa_path" \
--mount DB_ROOT="$REFERENCE_DISK" \
--env DB_PATH="$UNIREF90_PATH" \
--env N_CPU="$JACKHMMER_CPU" \
--env MAXSEQ="$UNIREF90_MAXSEQ")
job_ids+=( $uniref90_job_id )

echo "Starting Mgnify  on: $(date)" 
task=mgnify_search
logging_path="${output_path}/logging/${task}"
mgnify_output_msa_path="${output_path}/msas/${task}.sto"
mgnify_job_id=$(dsub \
--skip \
--name "$task" \
--command "$JACKHMMER_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$JACKHMMER_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input INPUT_PATH="$SEQUENCE" \
--output OUTPUT_PATH="$mgnify_output_msa_path" \
--mount DB_ROOT="$REFERENCE_DISK" \
--env DB_PATH="$MGNIFY_PATH" \
--env N_CPU="$JACKHMMER_CPU" \
--env MAXSEQ="$MGNIFY_MAXSEQ")
job_ids+=( $mgnify_job_id )

echo "Starting Uniclust search on: $(date)" 
task=uniclust30_search
logging_path="${output_path}/logging/${task}"
uniclust_output_msa_path="${output_path}/msas/${task}.a3m"
uniclust_job_id=$(dsub \
--skip \
--name "$task" \
--command "$HHBLITS_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input INPUT_PATH="$SEQUENCE" \
--output OUTPUT_PATH="$uniclust_output_msa_path" \
--mount DB_ROOT="$REFERENCE_DISK" \
--env DB_PATHS="$UNICLUST30_PATH" \
--env N_CPU="$HHBLITS_CPU" \
--env MAXSEQ="$UNICLUST30_MAXSEQ")
job_ids+=( $uniclust_job_id ) 

echo "Starting BFD search on: $(date)" 
task=bfd_search
logging_path="${output_path}/logging/${task}"
bfd_output_msa_path="${output_path}/msas/${task}.a3m"
bfd_job_id=$(dsub \
--skip \
--name "$task" \
--command "$HHBLITS_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input INPUT_PATH="$SEQUENCE" \
--output OUTPUT_PATH="$bfd_output_msa_path" \
--mount DB_ROOT="$REFERENCE_DISK" \
--env DB_PATHS="$BFD_PATH" \
--env N_CPU="$HHBLITS_CPU" \
--env MAXSEQ="$BFD_MAXSEQ")
job_ids+=( $bfd_job_id ) 

echo "Starting PDB search on: $(date)" 
task=pdb_search
logging_path="${output_path}/logging/${task}"
pdb_output_templates_path="${output_path}/templates/${task}.hhr"
pdb_output_features_path="${output_path}/features/${task}.pkl"
msa_input_path="$uniref_output_msa_path"
msa_data_format=sto
pdb_job_id=$(dsub \
--skip \
--name "$task" \
--command "$HHSEARCH_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input INPUT_SEQUENCE_PATH="$SEQUENCE" \
--input INPUT_MSA_PATH="$msa_input_path" \
--env MSA_DATA_FORMAT="$msa_data_format" \
--output OUTPUT_TEMPLATE_HITS_PATH="$pdb_output_templates_path" \
--output OUTPUT_TEMPLATE_FEATURES_PATH="$pdb_output_features_path" \
--mount DB_ROOT="$REFERENCE_DISK" \
--env DB_PATHS="$PDB70_PATH" \
--env MAXSEQ="$PDB_MAXSEQ" \
--env MMCIF_PATH="$PDB_MMCIF_PATH" \
--env OBSOLETE_PATH="$PDB_OBSOLETE_PATH" \
--env MAX_TEMPLATE_DATE="$MAX_TEMPLATE_DATE" \
--after "$uniref90_job_id" )
job_ids+=( $pdb_job_id )

echo "Starting feature aggregation on: $(date)" 
task=aggregate
logging_path="${output_path}/logging/${task}"
output_features_path="${output_path}/features/aggregated_features.pkl"
msas_path="${output_path}/msas"
aggregate_job_id=$(dsub \
--skip \
--name "$task" \
--command "$AGGREGATE_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$AGGREGATE_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--input-recursive MSAS_PATH="$msas_path" \
--input SEQUENCE_PATH="$SEQUENCE" \
--input TEMPLATE_FEATURES_PATH="$pdb_output_features_path" \
--output OUTPUT_FEATURES_PATH="$output_features_path" \
--after "${job_ids[@]}" \
--wait )


feature_engineering_end_time=$(date +%s)
echo "Feature engineering completed on: $(date)"
echo "Feature engineering elapsed time $(( $feature_engineering_end_time - $feature_engineering_start_time ))"

echo "Starting predictions on $(date)"
task=predict_relax
model_name=model_1
logging_path="${output_path}/logging/${task}"
raw_prediction_path="${output_path}/predictions/${model_name}_raw_prediction_.pkl"
unrelaxed_protein_path="${output_path}/proteins/${model_name}/unrelaxed_protein.pb"
relaxed_protein_path="${output_path}/proteins/${model_name}/relaxed_protein.pdb"
predict_job_id=$(dsub \
--name "$task" \
--command "$PREDICT_COMMAND" \
--provider "$DSUB_PROVIDER" \
--project "$PROJECT" \
--regions "$REGION" \
--logging "$logging_path" \
--image "$IMAGE" \
--machine-type "$PREDICT_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--accelerator-type "$PREDICT_ACCELERATOR_TYPE" \
--accelerator-count "$PREDICT_ACCELERATOR_COUNT" \
--input-recursive MODEL_PARAMS_PATH="$MODEL_PARAMS" \
--input FEATURES_PATH="$output_features_path" \
--env MODEL_NAME="$model_name" \
--env RANDOM_SEED=0 \
--env NUM_ENSEMBLE=1 \
--output RAW_PREDICTION_PATH="$raw_prediction_path" \
--output UNRELAXED_PROTEIN_PATH="$unrelaxed_protein_path" \
--output RELAXED_PROTEIN_PATH="$relaxed_protein_path" \
--env RELAX_USE_GPU="$RELAX_USE_GPU" \
--wait )


pipeline_end_time=$(date +%s)
echo "Pipeline completed on: $(date)"
echo "Pipeline elapsed time $(( $pipeline_end_time - $pipeline_start_time ))"








            


