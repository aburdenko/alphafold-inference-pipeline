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
import subprocess 
import shutil
import sys
import time

import pytest
#import mock

from typing import List


from alphafold_components.job_runner import JobRunner

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
    custom_job_spec = {
        'display_name': job_name,
        'job_spec': {
            'worker_pool_specs': [
                master_spec
            ],
            'network': NETWORK, 
        },
    }

    print('\n')
    job_runner = JobRunner(project=PROJECT, location=LOCATION) 
    result = job_runner.create_custom_job(job_name, custom_job_spec)
    print(result)

    job_runner.poll_job(result)

