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
import random
import logging
from re import I
import sys
import time
from datetime import datetime
import pprint
import json

from absl import flags
from absl import app

import google.cloud.aiplatform as aip

from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services.job_service import JobServiceClient

import google.auth




_PIPELINE_JOB_NAME = 'alphafold-inference'

FLAGS = flags.FLAGS

flags.DEFINE_string('project', 'jk-mlops-dev', 'project')
flags.DEFINE_string('project_number', '895222332033', 'project number')
flags.DEFINE_string('region', 'us-central1', 'region')
flags.DEFINE_string('nfs_server', '10.71.1.10', 'Filestore IP address')
flags.DEFINE_string('nfs_root_path', '/datasets_v1', 'NFS fileshare')
flags.DEFINE_string('mount_path', '/mnt/nfs/alphafold', 'NFS fileshare')
flags.DEFINE_string('package_path', 'gs://jk-alphafold-staging/packages/mytrainingcode-0.1.tar.gz', 'alphafold staging')

NFS_SERVER = '10.71.1.10'
NFS_ROOT_PATH = '/datasets_v1' 
MOUNT_PATH = '/mnt/nfs/alphafold' 
IMAGE = 'gcr.io/jk-mlops-dev/nfs-test'
SUBFOLDER='test'

MASTER_SPEC = {
  "machine_spec": {
    "machine_type": "n1-highmem-2",
  },
  "replica_count": 1,
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
        ],
    },
  }



def _main(argv):
 
    job_name = 'NFS_JOB_{}'.format(time.strftime("%Y%m%d_%H%M%S"))

    credentials, _ = google.auth.default()
    authed_session = google.auth.transport.requests.AuthorizedSession(credentials)
    endpoint = f'https://{FLAGS.region}-aiplatform.googleapis.com/v1beta1/projects/{FLAGS.project}/locations/{FLAGS.region}/customJobs'
    network = f'projects/{FLAGS.project_number}/global/networks/default' 

    custom_job = {
        "display_name": job_name,
        "job_spec": {    
            "worker_pool_specs": [
                MASTER_SPEC,
            ],
            "network": network,
        } 
    }

    pp=pprint.PrettyPrinter()
    pp.pprint(custom_job)

    response = authed_session.post(endpoint, data=json.dumps(custom_job))
    print('*************************')
    pp.pprint(response.json())



if __name__ == "__main__":
    app.run(_main)