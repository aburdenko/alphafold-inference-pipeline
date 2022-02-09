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

import subprocess

from kfp.v2 import dsl
from kfp.v2.dsl import Output

from alphafold_components.types.artifact_types import MSA

_REFERENCE_DATABASES_DISK_IMAGE = 'https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022'
_REFERENCE_DATABASES_DISK_SIZ = 3000
_UNIREF90_PATH = '/uniref90/uniref90.fasta'

@dsl.component(
    base_image='gcr.io/jk-mlops-dev/dsub',
    output_component_file='search_uniref90.yaml'
)
def search_uniref90(
    database_version: str,
    output_msa: Output[MSA] 
):
   """Searches the Uniref90 database.

   This is a simple prototype using dsub to submit a Cloud Life Sciences pipeline.
   We are using CLS as KFP does not support attaching pre-populated disks or premtible VMs.
   GCSFuse does not perform well with tools like hhsearch or hhblits.

   For now we are ignoring the database_version parameter. It could be used to
   attach  a specific prepopulated PD.
   """ 
   pass
   


    
