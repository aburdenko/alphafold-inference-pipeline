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
readonly PREDICT_MACHINE_TYPE=a2-highgpu-1g
readonly BOOT_DISK_SIZE=200

readonly JACKHMMER_CPU=8
readonly HHBLITS_CPU=12

readonly IMAGE=gcr.io/jk-mlops-dev/alphafold-components
readonly JACKHMMER_COMMAND='python /scripts/alphafold_runners/jackhmmer_runner.py'
readonly HHBLITS_COMMAND='python /scripts/alphafold_runners/hhblits_runner.py'
readonly HHSEARCH_COMMAND='python /scripts/alphafold_runners/hhsearch_runner.py'
readonly PREDICT_COMMAND='python /scripts/alphafold_runners/predict_runner.py'

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


# Process command line parameters
optstring=":hf:o:d:p:l:"
while getopts ${optstring} arg; do 
    case ${arg} in        
        f ) 
            sequence=$OPTARG
            ;;
        o )
            output_path=${OPTARG}
            ;;
        d ) 
            disk_image=${OPTARG}
            ;;
        p )
            project=${OPTARG}
            ;;
        l )
            location=${OPTARG}
            ;;
        h )
            usage
            ;;
        : ) 
            echo "Must supple an argument to -${OPTARG}" >&2 
            usage
            ;;
        ? )
            echo "Invalid option: -${OPTARG}" >&2
            usage
            ;;


    esac
done
shift $((OPTIND-1))
if [ ${#} != 0 ] || \
   [ -z ${sequence+x} ] || \
   [ -z ${output_path+x} ] || \
   [ -z ${disk_image+x} ] || \
   [ -z ${project+x} ] || \
   [ -z ${location+x} ]
then
    usage
fi

output_path=${output_path}/$(date +"%Y-%m-%d-%M-%S")
echo "Starting the pipeline on: $(date)"
echo "Pipeline outputs at: ${output_path}"
pipeline_start_time=$(date +%s)

echo "Starting feature engineering on: $(date)"
feature_engineering_start_time=$(date +%s)

task=search_uniref90
task_output=${output_path}/${task}
logging_path=${task_output}/logging
uniref_output_msa_path=${task_output}/msa/output.sto
echo "Starting Uniref90 search on: $(date)" 
uniref90_job_id=$(dsub \
--command "$JACKHMMER_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$JACKHMMER_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_PATH="$sequence" \
--output OUTPUT_PATH="$uniref_output_msa_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATH="$UNIREF90_PATH" \
--env N_CPU="$JACKHMMER_CPU" \
--env MAXSEQ="$UNIREF90_MAXSEQ" 
)
end_time=$(date +%s)
echo "Uniref90 search completed. Elapsed time $(( end_time - start_time ))"

task=search_mgnify
task_output=${output_path}/${task}
logging_path=${task_output}/logging
mgnify_output_msa_path=${task_output}/msa/output.sto
echo "Starting Mgnify search on: $(date)" 
start_time=$(date +%s)
mgnify_job_id=$(dsub \
--command "$JACKHMMER_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$JACKHMMER_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_PATH="$sequence" \
--output OUTPUT_PATH="$mgnify_output_msa_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATH="$MGNIFY_PATH" \
--env N_CPU="$JACKHMMER_CPU" \
--env MAXSEQ="$MGNIFY_MAXSEQ" 
)

task=search_uniclust
task_output=${output_path}/${task}
logging_path=${task_output}/logging
uniclust_output_msa_path=${task_output}/msa/output.a3m
echo "Starting Uniclust search on: $(date)" 
start_time=$(date +%s)
uniclust_job_id=$(dsub \
--command "$HHBLITS_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_PATH="$sequence" \
--output OUTPUT_PATH="$uniclust_output_msa_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATHS="$UNICLUST30_PATH" \
--env N_CPU="$HHBLITS_CPU" \
--env MAXSEQ="$UNICLUST30_MAXSEQ" 
)

task=search_bfd
task_output=${output_path}/${task}
logging_path=${task_output}/logging
bfd_output_msa_path=${task_output}/msa/output.a3m
echo "Starting BFD search on: $(date)" 
start_time=$(date +%s)
bfd_job_id=$(dsub \
--command "$HHBLITS_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_PATH="$sequence" \
--output OUTPUT_PATH="$bfd_output_msa_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATHS="$BFD_PATH" \
--env N_CPU="$HHBLITS_CPU" \
--env MAXSEQ="$BFD_MAXSEQ" 
)

task=search_pdb
task_output=${output_path}/${task}
logging_path=${task_output}/logging
pdb_output_templates_path=${task_output}/templates/output.hhr
pdb_output_features_path=${task_output}/features/output.pkl
msa_input_path=uniref_output_msa_path
msa_data_format=sto
echo "Starting PDB search on: $(date)" 
start_time=$(date +%s)
pdb_job_id=$(dsub \
--command "$HHBLITS_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$HHBLITS_MACHINE_TYPE" \
--boot-disk-size "$BOOT_DISK_SIZE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_SEQUENCE_PATH="$sequence" \
--input INPUT_MSA_PATH="$msa_input_path" \
--env MSA_DATA_FORMAT="$msa_data_format" \
--output OUTPUT_TEMPLATE_HITS_PATH="$pdb_output_templates_path" \
--output OUTPUT_TEMPLATE_FEATURES_PATH="$pdb_output_features_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATHS="$PDB70_PATH" \
--env MAXSEQ="$PDB_MAXSEQ" \
--env MMCIF_PATH="$PDB_MMCIF_PATH" \ 
--env OBSOLETE_PATH="$PDB_OBSOLETE_PATH" \
--after "$uniref90_job_id"
)








            

