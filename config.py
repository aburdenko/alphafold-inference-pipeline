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
PDB_MMCIF_PATH = 'pdb_mmcif/mmcif_files'
PDB_OBSOLETE_PATH = 'pdb_mmcif/obsolete.dat'
PDB_SEQRES_PATH = 'pdb_seqres/pdb_seqres.txt'

UNIREF90 = 'uniref90'
MGNIFY = 'mgnify'
BFD = 'bfd'
UNICLUST30 = 'uniclust30'
PDB70 = 'pdb70'
PDB_MMCIF = 'pdb_mmcif'
PDB_OBSOLETE = 'pdb_obsolete'
PDB_SEQRES = 'pdb_seqres'
UNIPROT = 'uniprot'

RELAX_MEMORY_LIMIT = os.getenv("MEMORY_LIMIT", "32G")
RELAX_CPU_LIMIT = os.getenv("CPU_LIMIT", "16")
RELAX_GPU_LIMIT = os.getenv("GPU_LIMIT", "2")
RELAX_GPU_TYPE = os.getenv("GPU_TYPE", "nvidia-tesla-t4")

MEMORY_LIMIT = os.getenv("MEMORY_LIMIT", "32G")
CPU_LIMIT = os.getenv("CPU_LIMIT", "16")
GPU_LIMIT = os.getenv("GPU_LIMIT", "2")
GPU_TYPE = os.getenv("GPU_TYPE", "nvidia-tesla-t4")
GKE_ACCELERATOR_KEY = 'cloud.google.com/gke-accelerator'


CLS_WRAPPERS_IMAGE = os.getenv("CLS_WRAPPER_IAMGE", 'gcr.io/jk-mlops-dev/cls-wrappers')
ALPHAFOLD_COMPONENTS_IMAGE = os.getenv("ALPHAFOLD_COMPONETS_IMAGE", 'gcr.io/jk-mlops-dev/alphafold-components')