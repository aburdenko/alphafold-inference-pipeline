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
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE,
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
    machine_type:str='c2-standard-16',
    boot_disk_size:int=200,
    n_cpu:int=12, 
    ):
    """Searches sequence databases using hhblits."""
    
    import logging
    import os
    import sys
    import time

    from alphafold.data import parsers
    from dsub_wrapper import run_dsub_job
    from job_runner import CustomJob

    _SUPPORTED_DATABASES = ['bfd', 'uniclust30']
    _ALPHAFOLD_RUNNER_IMAGE = 'gcr.io/aburdenko-project/alphafold'
    _SCRIPT = '/scripts/alphafold_runners/hhblits_runner.py'  


    for database in msa_dbs:
        if not (database in _SUPPORTED_DATABASES):
            raise RuntimeError(f'HHBlits cannot be used with {database} database.')

    database_paths = [reference_databases.metadata[database] for database in msa_dbs] 
    database_paths = ','.join(database_paths)

    nfs_server, nfs_root_path, mount_path, network = reference_databases.uri.split(',')
    params = {
        'INPUT_PATH': sequence.path,
        'OUTPUT_PATH': msa.path,
        'DB_ROOT': mount_path,
        'DB_PATHS': database_paths,
        'N_CPU': str(n_cpu),
        'MAXSEQ': str(maxseq)
    } 
    job_name = f'HHBLITS_JOB_{time.strftime("%Y%m%d_%H%M%S")}'
    t0 = time.time()
    logging.info('Starting database search...')
    custom_job = CustomJob.from_script_in_container(
        display_name=job_name,
        script_path=_SCRIPT,
        container_uri=_ALPHAFOLD_RUNNER_IMAGE,
        project=project,
        location=region,
        machine_type=machine_type,
        boot_disk_size_gb=boot_disk_size,
        nfs_server=nfs_server,
        nfs_root_path=nfs_root_path,
        mount_path=mount_path,
        env_variables=params,
    )
    custom_job.run(
       network=network
    ) 
    t1 = time.time()
    logging.info(f'Search completed. Elapsed time: {t1-t0}')

    with open(msa.path) as f:
        msa_str = f.read()
    parsed_msa = parsers.parse_a3m(msa_str)
    msa.metadata['data_format'] = 'a3m'  
    msa.metadata['num of sequences'] = len(parsed_msa.sequences) 

    

    
    



    
