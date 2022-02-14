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

import config

@dsl.component(
    base_image=config.CLS_WRAPPERS_IMAGE,
    output_component_file='component_msa_search.yaml'
)
def hhblits(
    project: str,
    region: str,
    msa_dbs: list,
    reference_databases: Input[Dataset],
    sequence: Input[Dataset],
    msa: Output[Dataset],
    cls_logging: Output[Artifact],
    maxseq:int=1_000_000,
    machine_type:str='c2-standard-32',
    boot_disk_size:int=200,
    n_cpu:int=32, 
    ):
    """Searches sequence databases using the specified tool.

    This is a simple prototype using dsub to submit a Cloud Life Sciences pipeline.
    We are using CLS as KFP does not support attaching pre-populated disks or premtible VMs.
    GCSFuse does not perform well with tools like hhsearch or hhblits.

    The prototype also lacks job control. If a pipeline step fails, the CLS job can get 
    orphaned

    """
    
    import logging
    import os
    import sys

    from dsub_wrapper import run_dsub_job

    _SUPPORTED_DATABASES = ['bfd', 'uniclust30']
    _DSUB_PROVIDER = 'google-cls-v2'
    _LOG_INTERVAL = '30s'
    _ALPHAFOLD_RUNNER_IMAGE = 'gcr.io/jk-mlops-dev/alphafold'
    _SCRIPT = '/scripts/alphafold_runners/hhblits_runner.py'  

    logging.basicConfig(format='%(asctime)s - %(message)s',
                      level=logging.INFO, 
                      datefmt='%d-%m-%y %H:%M:%S',
                      stream=sys.stdout)

    for database in msa_dbs:
        if not (database in _SUPPORTED_DATABASES):
            raise RuntimeError(f'HHBlits cannot be used with {database} database.')

    database_paths = [reference_databases.metadata[database] for database in msa_dbs] 
    database_paths = ','.join(database_paths)

    job_params = [
        '--machine-type', machine_type,
        '--boot-disk-size', str(boot_disk_size),
        '--logging', cls_logging.uri,
        '--log-interval', _LOG_INTERVAL, 
        '--image', _ALPHAFOLD_RUNNER_IMAGE,
        '--env', f'PYTHONPATH=/app/alphafold',
        '--mount', f'DB_ROOT={reference_databases.metadata["disk_image"]}',
        '--input', f'INPUT_PATH={sequence.uri}',
        '--output', f'OUTPUT_PATH={msa.uri}',
        '--env', f'DB_PATHS={database_paths}',
        '--env', f'N_CPU={n_cpu}',
        '--env', f'MAXSEQ={maxseq}', 
        '--script', _SCRIPT 
    ]

    result = run_dsub_job(
        provider=_DSUB_PROVIDER,
        project=project,
        regions=region,
        params=job_params,
    )

    msa.metadata['data_format'] = 'a3m'   

    

    
    



    
