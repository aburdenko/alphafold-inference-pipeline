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


SEQUENCE=gs://jk-alphafold-datasets-archive/fasta/T1050.fasta
TASK=T1050

readonly PROJECT=jk-mlops-dev
readonly REGION=us-central1
readonly OUTPUT_PATH="gs://jk-dsub-staging/benchmarks/optimized/${TASK}/pipeline"
readonly LOGGING="gs://jk-dsub-staging/benchmarks/optimized/${TASK}"
readonly SCRIPT=run_alphafold_inference.sh
readonly REFERENCE_DISK="https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
readonly MAX_TEMPLATE_DATE=2020-05-14
readonly MODEL_PARAMS=gs://jk-alphafold-datasets-archive/jan-22/params
readonly IMAGE=gcr.io/jk-mlops-dev/dsub



dsub --provider google-cls-v2 \
 --name "$TASK" \
 --project "$PROJECT" \
 --image "$IMAGE" \
 --regions "$REGION" \
 --logging "$LOGGING" \
 --script "$SCRIPT" \
 --env PROJECT="$PROJECT" \
 --env REGION="$REGION" \
 --env SEQUENCE="$SEQUENCE" \
 --env OUTPUT_PATH="$OUTPUT_PATH" \
 --env MAX_TEMPLATE_DATE="$MAX_TEMPLATE_DATE" \
 --env REFERENCE_DISK="$REFERENCE_DISK" \
 --env MODEL_PARAMS="$MODEL_PARAMS"