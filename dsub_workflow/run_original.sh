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


FASTA=gs://gs://jk-alphafold-datasets-archive/fasta/T1050.fasta
TASK=T1050

readonly PROJECT_ID=jk-mlops-dev
readonly REGION=us-central1
readonly LOGGING="gs://jk-dsub-staging/benchmarks/logging/${TASK}"
readonly OUTPUT_PATH="gs://jk-dsub-staging/benchmarks/output${TASK}"
readonly IMAGE=gcr.io/jk-mlops-dev/alphafold-components
readonly SCRIPT=original.sh
readonly DISK_IMAGE="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
readonly MACHINE_TYPE=a2-highgpu-1g
readonly BOOT_DISK_SIZE=200
readonly ACCELERATOR_TYPE=nvidia-tesla-a100
readonly ACCELERATOR_COUNT=1


dsub --provider google-cls-v2 \
 --name "$TASK" \
 --project "$PROJECT_ID" \
 --regions "$REGION" \
 --logging "$LOGGING" \
 --image "$IMAGE" \
 --script "$SCRIPT" \
 --input FASTA="$FASTA" \
 --mount DB="$DISK_IMAGE" \
 --output-recursive OUT_PATH="$OUTPUT_PATH" \
 --machine-type "$MACHINE_TYPE" \
 --boot-disk-size "$BOOT_DISK_SIZE" \
 --accelerator-type "$ACCELERATOR_TYPE" \
 --accelerator-count "$ACCELERATOR_COUNT" 
