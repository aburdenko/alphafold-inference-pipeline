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

import os

PIPELINE_NAME = 'alphafold-inference'
PIPELINE_DESCRIPTION = 'Alphafold inference'

REFERENCE_DATASETS_IMAGE = "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
REFERENCE_DATASETS_GCS_LOCATION = 'gs://jk-alphafold-datasets-archive/jan-22'
MODEL_PARAMS_GCS_LOCATION='gs://jk-alphafold-datasets-archive/jan-22/params'

UNIREF90_PATH = 'uniref90/uniref90.fasta'
MGNIFY_PATH = 'mgnify/mgy_clusters_2018_12.fa'
BFD_PATH = 'bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'
UNICLUST30_PATH = 'uniclust30/uniclust30_2018_08/uniclust30_2018_08'
UNIPROT_PATH = 'uniprot/uniprot.fasta'
PDB70_PATH = 'pdb70/pdb70'
PDB_MMCIF = 'pdb_mmcif/mmcif_files'
PDB_OBSOLETE_PATH = 'pdb_mmcif/obsolete.dat'
PDB_SEQRES_PATH = 'pdb_seqres/pdb_seqres.txt'

MEMORY_LIMIT = os.getenv("MEMORY_LIMIT", "120G")
CPU_LIMIT = os.getenv("CPU_LIMIT", "32")
GPU_LIMIT = os.getenv("GPU_LIMIT", "4")
GPU_TYPE = os.getenv("GPU_TYPE", "nvidia-tesla-t4")
GKE_ACCELERATOR_KEY = 'cloud.google.com/gke-accelerator'