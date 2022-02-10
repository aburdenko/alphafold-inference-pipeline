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

from re import I
import subprocess

from kfp.v2 import dsl
from kfp.v2.dsl import Output

from alphafold_components.artifact_types import MSA


@dsl.component(
    base_image='gcr.io/jk-mlops-dev/alphafold-components'
)
def db_search(
    project: str,
    region: str,
    datasets_disk_image: str,
    database_paths: str,
    fasta_path: str,
    search_tool: str,
    output_msa: Output[MSA], 
    tool_options: dict=None):
    """Searches sequence databases using the specified tool.

    This is a simple prototype using dsub to submit a Cloud Life Sciences pipeline.
    We are using CLS as KFP does not support attaching pre-populated disks or premtible VMs.
    GCSFuse does not perform well with tools like hhsearch or hhblits.

    """

    import logging

    from alphafold_components import dsub_wrapper

    # For a prototype we are hardcoding some values. Whe productionizing
    # we can make them compile time or runtime parameters
    # E.g. CPU type is important. HHBlits requires at least SSE2 instruction set
    # Works better with AVX2. 
    # At runtime we could pass them as tool_options dictionary

    _REFERENCE_DATASETS_IMAGE = '"https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"'
    _TOOL_TO_SETTINGS_MAPPING = {
       'jackhmmer': {
           'MACHINE_TYPE': 'n1-standard-8',
           'BOOT_DISK_SIZE': '200',
           'N_CPU': 6,
           'MAX_STO_SEQUENCES': '10_000'
       },
       'hhblits': {
           'MACHINE_TYPE': 'c2-standard-8',
           'BOOT_DISK_SIZE': '200',
           'N_CPU': 6,
       },
       'hhsearch': {
           'MACHINE_TYPE': 'c2-standard-8',
           'BOOT_DISK_SIZE': '200',
           'MAXSEQ': '1_000_000'
       }
    }

    if not search_tool in _TOOL_TO_SETTINGS_MAPPING.keys():
        raise ValueError(f'Unsupported tool: {search_tool}')
    # We should probably also do some checking whether a given tool, DB combination works

    _DSUB_PROVIDER = 'google_cls_v2'
    _LOG_INTERVAL = '30s'
    _SCRIPT = './msa_runner.py'
    
    
    # This is a temporary hack till we find a better option for dsub logging location
    # It would be great if we can access pipeline root directly
    # If not we can always pass the location as a parameter 
    logging_gcs_path = output_msa.uri.split('/')[2:-2]
    folders = '/'.join(logging_gcs_path)
    logging_gcs_path = f'gs://{folders}/logging'
    
    dsub_job = dsub_wrapper.DsubJob(
        project=project,
        region=region,
        logging=logging_gcs_path,
        provider=_DSUB_PROVIDER,
        machine_type=_TOOL_TO_SETTINGS_MAPPING[search_tool].pop('MACHINE_TYPE'),
        boot_disk_size=_TOOL_TO_SETTINGS_MAPPING[search_tool].pop('BOOT_DISK_SIZE'),
        log_interval=_LOG_INTERVAL
    )

    inputs = {
        'FASTA_PATH': fasta_path, 
    }
    outputs = {
        'OUTPUT_DIR': output_msa.uri,
    }
    env_vars = {
        'PYTHONPATH': '/app/alphafold',
        'DATABASE_PATHS': database_paths,
        'MSA_TOOL': search_tool,
    }
    env_vars.update(_TOOL_TO_SETTINGS_MAPPING[search_tool])

    if not datasets_disk_image:
        datasets_disk_image = _REFERENCE_DATASETS_IMAGE

    disk_mounts = {
        'DATABASES_ROOT': datasets_disk_image 
    }

    logging('Starting a dsub job')
    # Right now this is a blocking call. In future we should implement
    # a polling loop to periodically retrieve logs, stdout and stderr
    # and push it Vertex
    result = dsub_job.run_job(
        scripts=_SCRIPT,
        inputs=inputs,
        outputs=outputs,
        env_vars=env_vars,
        disk_mounts=disk_mounts
    )
    
    logging.info('Job completed')
    logging.info(f'Completion status {result.returncode}')
    logging.info(f'Logs: {result.stdout}')
    

    
    



    
