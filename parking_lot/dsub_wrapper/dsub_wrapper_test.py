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



import base64
import datetime
import logging
import json
import mock
import pytest
import time
import sys

_dsub_binary_path = shutil.which('dsub')
_project='jk-mlops-dev'
_region = 'us-central1'
_logging = 'gs://jk-dsub-staging/logging'
_provider = 'google-cls-v2'
_boot_disk_size = 100
_base_bucket = 'gs://jk-dsub-staging'
_alphafold_datasets = "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"

logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

def test_jackhmmer_job():
    
    _log_interval = '30s'
    _image = 'gcr.io/jk-mlops-dev/alphafold'
    _machine_type = 'n1-standard-4'
    _databases =  'uniref90/uniref90.fasta'

    dsub = DsubJob(binary_path=_dsub_binary_path,
                project=_project,
                image=_image,
                region=_region,
                logging=_logging,
                provider=_provider,
                machine_type=_machine_type,
                boot_disk_size=_boot_disk_size,
                log_interval=_log_interval)

    _script = './alphafold_runners/msa_runner.py'
    _inputs = {
        'FASTA_PATH': f'{_base_bucket}/fasta/T1050.fasta', 
        }
    _outputs = {
        'OUTPUT_DIR': f'{_base_bucket}/output/jackhmmer'
    }
    _env_vars = {
        'PYTHONPATH': '/app/alphafold',
        'DATABASE_PATHS': _databases,
        'MSA_TOOL': 'jackhmmer',
        'N_CPU': '4',
        'MAX_STO_SEQUENCES': '10000',
        }
    _disk_mounts = {'DATABASES_ROOT': _alphafold_datasets}
    print('Starting jackhmmer job')
    result = dsub.run_job(script=_script,
                inputs=_inputs,
                outputs=_outputs,
                env_vars=_env_vars,
                disk_mounts=_disk_mounts)

    print(result.returncode)
    print(result.stderr)
    print(result.stdout)


def test_hhblits_job():
    
    _log_interval = '30s'
    _image = 'gcr.io/jk-mlops-dev/alphafold'
    _machine_type = 'c2-standard-8'
    _boot_disk_size = 500
    _databases =  'uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'

    dsub = DsubJob(binary_path=_dsub_binary_path,
                project=_project,
                image=_image,
                region=_region,
                logging=_logging,
                provider=_provider,
                machine_type=_machine_type,
                boot_disk_size=_boot_disk_size,
                log_interval=_log_interval)

    _script = './alphafold_runners/msa_runner.py'
    _inputs = {
        'FASTA_PATH': f'{_base_bucket}/fasta/T1050.fasta', 
        }
    _outputs = {
        'OUTPUT_DIR': f'{_base_bucket}/output/hhblits'
    }
    _env_vars = {
        'PYTHONPATH': '/app/alphafold',
        'DATABASE_PATHS': _databases,
        'MSA_TOOL': 'hhblits',
        'N_CPU': '4',
        }
    _disk_mounts = {'DATABASES_ROOT': _alphafold_datasets}
    print('Starting hhblits job')
    result = dsub.run_job(script=_script,
                inputs=_inputs,
                outputs=_outputs,
                env_vars=_env_vars,
                disk_mounts=_disk_mounts)

    print(result.returncode)
    print(result.stderr)
    print(result.stdout)

def test_hhsearch_job():
    
    _log_interval = '30s'
    _image = 'gcr.io/jk-mlops-dev/alphafold'
    _machine_type = 'c2-standard-8'
    _databases =  'pdb70/pdb70'
    _boot_disk_size = 500

    dsub = DsubJob(binary_path=_dsub_binary_path,
                project=_project,
                image=_image,
                region=_region,
                logging=_logging,
                provider=_provider,
                machine_type=_machine_type,
                boot_disk_size=_boot_disk_size,
                log_interval=_log_interval)

    _script = './alphafold_runners/template_runner.py'
    _inputs = {
        'MSA_PATH': f'{_base_bucket}/msas/uniref90_results.sto', 
        }
    _outputs = {
        'OUTPUT_DIR': f'{_base_bucket}/output/hhsearch'
    }
    _env_vars = {
        'PYTHONPATH': '/app/alphafold',
        'DATABASE_PATHS': _databases,
        'TEMPLATE_TOOL': 'hhsearch',
        'MAXSEQ': '1_000_000',
        }
    _disk_mounts = {'DATABASES_ROOT': _alphafold_datasets}
    print('Starting hhsearch job')
    result = dsub.run_job(script=_script,
                inputs=_inputs,
                outputs=_outputs,
                env_vars=_env_vars,
                disk_mounts=_disk_mounts)

    print(result.returncode)
    print(result.stderr)
    print(result.stdout)


