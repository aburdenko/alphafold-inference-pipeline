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
from re import I

from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset

import config

@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE,
    output_component_file='component_template_search.yaml'
)
def hhsearch(
    project: str,
    region: str,
    template_dbs: list,
    mmcif_db: str,
    obsolete_db: str,
    max_template_date: str,
    reference_databases: Input[Dataset],
    sequence: Input[Dataset],
    msa: Input[Dataset],
    template_hits: Output[Dataset],
    template_features: Output[Dataset],
    cls_logging: Output[Artifact],
    maxseq:int=1_000_000,
    max_template_hits:int=20, 
    machine_type:str='c2-standard-8',
    boot_disk_size:int=200,
    ):
    """Searches for protein templates """
    
    import logging
    import os
    import sys
    import time

    from alphafold.data import parsers
    from job_runner import CustomJob
    from dsub_wrapper import run_dsub_job

    _ALPHAFOLD_RUNNER_IMAGE = 'gcr.io/jk-mlops-dev/alphafold-components'
    _SCRIPT = '/scripts/alphafold_runners/hhsearch_runner.py'
   
    logging.basicConfig(format='%(asctime)s - %(message)s',
                      level=logging.INFO, 
                      datefmt='%d-%m-%y %H:%M:%S',
                      stream=sys.stdout)

    database_paths = [reference_databases.metadata[database]
                      for database in template_dbs]
    database_paths = ','.join(database_paths)

    nfs_server, nfs_root_path, mount_path, network = reference_databases.uri.split(',')
    params = {
        'INPUT_SEQUENCE_PATH': sequence.uri,
        'INPUT_MSA_PATH': msa.uri,
        'MSA_DATA_FORMAT': msa.metadata['data_format'],
        'OUTPUT_TEMPLATE_HITS_PATH': template_hits.uri,
        'OUTPUT_TEMPLATE_FEATURES_PATH': template_features.uri,
        'DB_ROOT': mount_path,
        'DB_PATHS': database_paths,
        'MMCIF_PATH': reference_databases.metadata[mmcif_db],
        'OBSOLETE_PATH': reference_databases.metadata[obsolete_db],
        'MAXSEQ': str(maxseq),
        'MAX_TEMPLATE_HITS': str(max_template_hits),
        'MAX_TEMPLATE_DATE': max_template_date,
    } 
    job_name = f'JACKHMMER_JOB_{time.strftime("%Y%m%d_%H%M%S")}'
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
    
    with open(template_hits.path) as f:
        hhr_str = f.read()
    parsed_hhr = parsers.parse_hhr(hhr_str)
    template_hits.metadata['data_format'] = 'hhr'
    template_hits.metadata['num of hits'] = len(parsed_hhr)
    template_features.metadata['data_format'] = 'pkl' 

    

    
    



    
