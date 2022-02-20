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


import logging
import os
from re import L
import pprint
import subprocess 
import shutil
import sys
import time
from turtle import st

import pytest
#import mock

from typing import List


from alphafold_components.job_runner import CustomJob 

PROJECT='jk-mlops-dev'
PROJECT_NUMBER='895222332033'
LOCATION='us-central1'

NFS_SERVER = '10.71.1.10'
NFS_ROOT_PATH = '/datasets_v1' 
MOUNT_PATH = '/mnt/nfs/alphafold' 
IMAGE = 'gcr.io/jk-mlops-dev/nfs-test'
SUBFOLDER='test'
SLEEP_TIME=120
NETWORK = f'projects/{PROJECT_NUMBER}/global/networks/default' 

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO, 
                    datefmt='%d-%m-%y %H:%M:%S',
                    stream=sys.stdout)

def test_create_job():


    master_spec = {
        'machine_spec': {
            'machine_type': 'n1-standard-8'
        },
        'replica_count': 1,
        "nfs_mounts": [{
            "server": NFS_SERVER,
            "path": NFS_ROOT_PATH,
            "mount_point": MOUNT_PATH,
        }],
        "container_spec": {
            "image_uri": IMAGE,
            "command": ["python"],
            "args": [ "task.py",
                f"--mount_root_path={MOUNT_PATH}",
                f"--subfolder={SUBFOLDER}",
                f"--sleep_time={SLEEP_TIME}",
            ],
        },
    }      

    job_name = 'NFS_JOB_{}'.format(time.strftime("%Y%m%d_%H%M%S"))
 
    print('\n')
    job_runner = CustomJob(
        display_name=job_name,
        project=PROJECT, 
        location=LOCATION, 
        worker_pool_specs=[master_spec]) 
    result = job_runner._create_custom_job()
    print(result)

    job_runner._poll_job(result)


def test_from_script_in_container():

    job_name = 'NFS_JOB_{}'.format(time.strftime("%Y%m%d_%H%M%S"))
    script_path = '/scripts/alphafold_runners/jackhmmer_runner.py'
    container_uri = 'gcr.io/jk-mlops-dev/alphafold'
    project = PROJECT 
    location = LOCATION
    staging_bucket = 'gs://jk-alphafold-staging/staging'
    machine_type = 'n1-standard-8'
    nfs_server = NFS_SERVER
    nfs_root_path = NFS_ROOT_PATH
    mount_path = MOUNT_PATH
    env_variables = {
        'INPUT_PATH': '/gcs/jk-alphafold-datasets-archive/fasta/T1044.fasta',
        'OUTPUT_PATH': '/gcs/jk-alphafold-staging/outputs/testing/output.sto',
        'DB_ROOT': mount_path,
        'DB_PATH': 'uniref90/uniref90.fasta'
    }


    custom_job = CustomJob.from_script_in_container(
        display_name=job_name,
        script_path=script_path,
        container_uri=container_uri,
        project=project,
        location=location,
        staging_bucket=staging_bucket,
        machine_type=machine_type,
        nfs_server=nfs_server,
        nfs_root_path=nfs_root_path,
        mount_path=mount_path,
        env_variables=env_variables,
    )

    pp=pprint.PrettyPrinter()
    pp.pprint(custom_job.custom_job_spec)

    custom_job.run(
       network=NETWORK
    )
