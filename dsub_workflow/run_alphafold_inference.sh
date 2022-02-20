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
readonly POLLING_INTERVAL=30s
readonly JACKHMMER_MACHINE_TYPE=n1-standard-8
readonly HHBLITS_MACHINE_TYPE=c2-standard-16
readonly HHSEARCH_MACHINE_TYPE=c2-standard-16
readonly PREDICT_MACHINE_TYPE=a2-highgpu-1g



# Process command line parameters
optstring=":hf:o:d:l:"
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
if [ ${#} != 0 ] || [ -z ${sequence+x} ] || [ -z ${output_path+x} ] || [ -z ${disk_image+x} ]; then
    usage
fi


output_path=${output_path}/$(date +"%Y-%m-%d-%M-%S")

echo $output_path

echo 'Starting Uniref90 search ...'



            


