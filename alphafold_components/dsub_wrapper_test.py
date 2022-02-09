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
"""A Python wrapper around dsub."""


import os
import subprocess 
import shutil

from dsub_wrapper import DsubJob

_dsub_binary_path = shutil.which('dsub')
_project='jk-mlops-dev'
_region = 'us-central1'
_logging = 'gs://jk-dsub-staging/logging'
_provider = 'google-cls-v2'
_boot_disk_size = 100
_log_interval = '30s'
_image = 'gcr.io/jk-mlops-dev/alphafold'
_machine_type = 'n1-standard-4' 

dsub = DsubJob(binary_path=_dsub_binary_path,
               project=_project,
               image=_image,
               region=_region,
               logging=_logging,
               provider=_provider,
               machine_type=_machine_type,
               boot_disk_size=_boot_disk_size,
               log_interval=_log_interval)

_script = './alphafold_runners/runner_test.py'
_inputs = {'FASTA_PATH': 'gs://jk1-', 'N_CPU': '2'}
_inputs = {}
_outputs = {}
_env_vars = {'PYTHONPATH': '/app/alphafold'}
_disk_mounts = {'DB': "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/alphafold-datasets-jan-2022 3000"}
result = dsub.run_job(script=_script,
             inputs=_inputs,
             outputs=_outputs,
             env_vars=_env_vars,
             disk_mounts=_disk_mounts)

print(result.returncode)
print(result.stderr)
print(result.stdout)




