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

readonly UNIREF_MAXSEQ=10_000


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

task=search_uniref90
task_output=${output_path}/${task}
logging_path=${task_output}/logging
output_msa_path=${task_output}/msa/output.sto

echo "Starting Uniref90 search on: $(date)" 
start_time=$(date +%s)
uniref90_job_id=$(dsub \
--command "$JACKHMMER_COMMAND" \
--provider "$DSUB_PROVIDER" \
--image "$IMAGE" \
--machine-type "$JACKHMMER_MACHINE_TYPE" \
--project "$project" \
--regions "$location" \
--logging "$logging_path" \
--input INPUT_PATH="$sequence" \
--output OUTPUT_PATH="$output_msa_path" \
--mount DB_ROOT="$disk_image" \
--env DB_PATH="$UNIREF90_PATH" \
--env N_CPU="$JACKHMMER_CPU" \
--env MAXSEQ="$UNIREF_MAXSEQ" \
)
end_time=$(date +%s)
echo "Uniref90 search completed. Elapsed time $(( end_time - start_time ))"

echo $uniref90_job_id




            


