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


import json
import logging
import os
from re import I
import subprocess 
import shutil
import sys
import time

from typing import List, Optional, Dict

from google.cloud.aiplatform_v1 import JobServiceClient
from google.cloud.aiplatform_v1.types import job_state as gca_job_state

from google.cloud.aiplatform.utils import source_utils
from google.cloud.aiplatform.utils import worker_spec_utils

import google.auth
from google.protobuf import json_format

#from  alphafold_components import execution_context
import execution_context

_POLLING_INTERVAL_IN_SECONDS = 60 
_CONNECTION_ERROR_RETRY_LIMIT = 5

_JOB_COMPLETE_STATES = (
    gca_job_state.JobState.JOB_STATE_SUCCEEDED,
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
    gca_job_state.JobState.JOB_STATE_PAUSED,
)

_JOB_ERROR_STATES = (
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
    gca_job_state.JobState.JOB_STATE_PAUSED,
)

#_RUNNER_CONFIG = {
#    Runners.JACKHMMER: {'script': '/scripts/alphafold_runners/jackhmmer_runner.py'},
#    Runners.HHSEARCH: {'script': '/scripts/alphafold_runners/hhserach_runner.py'},
#    Runners.HHBLITS: {'script': '/scripts/alphafold_runners/hhblits_runner.py'}
#}


class CustomJob():
    """Common module for creating and polling custom Vertex jobs.

    Since we are using NFS support that is still not implemented in 
    the official SDK we are calling REST API directly
    """

    def __init__(
        self,
        display_name: str, 
        worker_pool_specs: dict,
        project: str, 
        location: str,
        ):
        """Initializes a job client and other common attributes."""
        self.project = project
        self.location = location
        self.client_options = {
            'api_endpoint': f'{location}-aiplatform.googleapis.com'
        }
        self.job_client = JobServiceClient(
            client_options=self.client_options
        )
        self.custom_job_spec = {
            'display_name': display_name,
            'job_spec': {
                'worker_pool_specs': worker_pool_specs,
            }
        }

    def check_if_job_exists(self) -> Optional[str]:
        """Check if the job already exists."""
        pass

   
    # For now we have to call the REST API directly as SDK does not support 
    # NFS mount section
    def _create_custom_job(self) -> str:
        """Create a job."""

        credentials, _ = google.auth.default()
        authed_session = google.auth.transport.requests.AuthorizedSession(credentials)
        job_uri = f'https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project}/locations/{self.location}/customJobs'
        response = authed_session.post(job_uri, data=json.dumps(self.custom_job_spec))

        if response.status_code != 200:
            raise RuntimeError(f'Request failed: {response.json()}')

        return response.json()['name']
    

    #def create_custom_job(self, job_name: str, custom_job_spec: dict) -> str:
    #    """Create a job."""
    #    parent = f'projects/{self.project}/locations/{self.location}'

    #    create_job_response = self.job_client.create_custom_job(
    #        parent=parent,
    #        custom_job=custom_job_spec
    #    )

    #    job_name = create_job_response.name

    #    return job_name 


    def _poll_job(self, job_name: str):
        """Poll the job status."""
        with execution_context.ExecutionContext(
            on_cancel=lambda: self.send_cancel_request(job_name)):
            retry_count = 0
            while True:
                try:
                    get_job_response = self.job_client.get_custom_job(name=job_name) 
                    retry_count = 0
                # Handle transient connection error.
                except ConnectionError as err:
                    retry_count += 1
                    if retry_count < _CONNECTION_ERROR_RETRY_LIMIT:
                        logging.warning(
                            'ConnectionError (%s) encountered when polling job: %s. Trying to '
                            'recreate the API client.', err, job_name)
                        # Recreate the Python API client.
                        self.job_client = JobServiceClient(
                            self.client_options)
                    else:
                        logging.error('Request failed after %s retries.',
                                        _CONNECTION_ERROR_RETRY_LIMIT)
                        # TODO(ruifang) propagate the error.
                        raise

                if get_job_response.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED:
                    logging.info('Job completed successfully =%s', get_job_response.state)
                    return get_job_response
                elif get_job_response.state in _JOB_ERROR_STATES:
                    raise RuntimeError(f'Job failed with error state: {get_job_response.state}.')
                else:
                    logging.info(
                        'Job %s is running:  %s.'
                        ' Waiting for %s seconds for next poll.', job_name,
                        get_job_response.state, _POLLING_INTERVAL_IN_SECONDS)
                    time.sleep(_POLLING_INTERVAL_IN_SECONDS)

    def _send_cancel_request(self, job_name: str):
        if not job_name:
            return

        self.job_client.cancel_custom_job(job_name)
    

    def run(
            self,
            service_account: Optional[str] = None,
            network: Optional[str] = None,
            timeout: Optional[int] = None,
            sync: bool = True,
        ) -> None:

            """Run this configured CustomJob."""
            
            self.custom_job_spec['job_spec']['network'] = network
            result = self._create_custom_job()
            self._poll_job(result)
            


    @classmethod
    def from_script_in_container(
        cls,
        display_name: str,
        script_path: str,
        container_uri: str,
        project: str,
        location: str,
        env_variables: Optional[Dict[str, str]] = None,
        machine_type: str = 'n1-standard-8',
        accelerator_type: str = 'ACCELERATOR_TYPE_UNSPECIFIED',
        accelerator_count: int = 0,
        boot_disk_type: str = 'pd-ssd',
        boot_disk_size_gb: int = 100,
        nfs_server: str = None,
        nfs_root_path: str = None,
        mount_path: str = None,
    ) -> "CustomJob":
        
        worker_pool_specs = worker_spec_utils._DistributedTrainingSpec.chief_worker_pool(
            replica_count=1,
            machine_type=machine_type,
            accelerator_count=accelerator_count,
            accelerator_type=accelerator_type,
            boot_disk_type=boot_disk_type,
            boot_disk_size_gb=boot_disk_size_gb,
        ).pool_specs

        if nfs_server and nfs_root_path and mount_path:
            worker_pool_specs[0]['nfs_mounts'] = [{
                'server': nfs_server,
                'path': nfs_root_path,
                'mount_point': mount_path,
            }]

        container_spec = {
            'image_uri': container_uri,
            'command': ['python'],
            'args': [script_path],
        }
        
        if env_variables:
            env = [{'name': name, 'value': value} for name, value in env_variables.items()]
            container_spec['env'] = env
        worker_pool_specs[0]['container_spec'] = container_spec


        return cls(
            display_name=display_name,
            worker_pool_specs=worker_pool_specs,
            project=project,
            location=location,
        )



