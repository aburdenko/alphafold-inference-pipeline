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

from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset


_ALPHAFOLD_RUNNER_IMAGE = os.getenv('ALPHAFOLD_RUNNER_IAMGE', 'gcr.io/jk-mlops-dev/alphafold')
_COMPONENTS_IMAGE = os.getenv('COMPONENTS_IMAGE', 'gcr.io/jk-mlops-dev/alphafold-components')


@dsl.component(
    base_image=_COMPONENTS_IMAGE,
    output_component_file='component_db_search.yaml'
)
def db_search(
    project: str,
    region: str,
    disk_image: str,
    database_paths: str,
    db_tool: str,
    input_data: Input[Dataset],
    output_data: Output[Dataset],
    cls_logging: Output[Artifact] 
    ):
    """Searches sequence databases using the specified tool.

    This is a simple prototype using dsub to submit a Cloud Life Sciences pipeline.
    We are using CLS as KFP does not support attaching pre-populated disks or premtible VMs.
    GCSFuse does not perform well with tools like hhsearch or hhblits.

    """
    

    import logging
    import os
    import sys

    from dsub_wrapper import run_dsub_job

    # For a prototype we are hardcoding some values. Whe productionizing
    # we can make them compile time or runtime parameters
    # E.g. CPU type is important. HHBlits requires at least SSE2 instruction set
    # Works better with AVX2. 
    # At runtime we could pass them as tool_options dictionary

    logging.basicConfig(format='%(asctime)s - %(message)s',
                      level=logging.INFO, 
                      datefmt='%d-%m-%y %H:%M:%S',
                      stream=sys.stdout)

    _TOOL_TO_SETTINGS_MAPPING = {
       'jackhmmer': {
           'MACHINE_TYPE': 'n1-standard-4',
           'BOOT_DISK_SIZE': '200',
           'N_CPU': 4,
           'MAXSEQ': '10_000',
           'INPUT_DATA_FORMAT': 'fasta',
           'OUTPUT_DATA_FORMAT': 'sto',
           'SCRIPT': '/scripts/alphafold_components/alphafold_runners/db_search_runner.py' 
       },
       'hhblits': {
           'MACHINE_TYPE': 'c2-standard-4',
           'BOOT_DISK_SIZE': '200',
           'N_CPU': 4,
           'MAXSEQ': '1_000_000',
           'INPUT_DATA_FORMAT': 'fasta',
           'OUTPUT_DATA_FORMAT': 'a3m',
           'SCRIPT': '/scripts/alphafold_components/alphafold_runners/db_search_runner.py' 
       },
       'hhsearch': {
           'MACHINE_TYPE': 'c2-standard-4',
           'BOOT_DISK_SIZE': '200',
           'N_CPU': 0, # Not setable for hhsearch
           'MAXSEQ': '1_000_000',
           'INPUT_DATA_FORMAT': 'sto',
           'OUTPUT_DATA_FORMAT': 'hhr',
           'SCRIPT': '/scripts/alphafold_components/alphafold_runners/db_search_runner.py' 
       }
    }

    if not db_tool in _TOOL_TO_SETTINGS_MAPPING.keys():
        raise ValueError(f'Unsupported tool: {db_tool}')
    # We should probably also do some checking whether a given tool, DB combination works

    _DSUB_PROVIDER = 'google-cls-v2'
    _LOG_INTERVAL = '30s'
    _IMAGE = 'gcr.io/jk-mlops-dev/alphafold'

    output_data.metadata['data_format'] = _TOOL_TO_SETTINGS_MAPPING[db_tool]['OUTPUT_DATA_FORMAT']
    
    job_params = [
        '--db_tool', db_tool,
        '--machine-type', _TOOL_TO_SETTINGS_MAPPING[db_tool]['MACHINE_TYPE'],
        '--boot-disk-size', _TOOL_TO_SETTINGS_MAPPING[db_tool]['BOOT_DISK_SIZE'],
        '--logging', cls_logging.uri,
        '--mount', f'DB_ROOT={disk_image}',
        '--input', f'INPUT_DATA={input_data.uri}',
        '--output', f'OUTPUT_DATA={output_data.uri}',
        '--env', f'DB_PATHS={database_paths}',
        '--env', f'N_CPU={_TOOL_TO_SETTINGS_MAPPING[db_tool]["N_CPU"]}',
        '--env', f'INPUT_DATA_FORMAT={_TOOL_TO_SETTINGS_MAPPING[db_tool]["INPUT_DATA_FORMAT"]}', 
        '--env', f'OUTPUT_DATA_FORMAT={_TOOL_TO_SETTINGS_MAPPING[db_tool]["OUTPUT_DATA_FORMAT"]}', 
        '--env', f'MAXSEQ={_TOOL_TO_SETTINGS_MAPPING[db_tool]["MAXSEQ"]}', 
        '--script', _TOOL_TO_SETTINGS_MAPPING[db_tool]['SCRIPT'] 
    ]

    return

    result = run_dsub_job(
        provider='google-cls-v2',
        project=project,
        regions=region,
        params=job_params,
    ) 

    

    
    



    
