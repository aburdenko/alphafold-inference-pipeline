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

from typing import List

_DSUB_BINARY_PATH = shutil.which('dsub')
_DSTAT_BINARY_PATH = shutil.which('dstat')
_POLLING_INTERVAL = 15


def run_dsub_job(params: List[str],
                 provider: str='local',
                 project: str=None,
                 regions: str=None):
    """Launches and monitors dsub job."""


    if '--wait' in params:
        params.remove('--wait')

    logging.info(f'Executing dsub with the following params: {params}')

    dsub_cmd = [
        _DSUB_BINARY_PATH,
        '--provider', provider] + params
 
    if provider == 'google-cls-v2':
        dsub_cmd += ['--project', project, '--regions', regions]

    dsub_cmd += ['--wait', '--summary']
        
    result = subprocess.run(
        dsub_cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    if result.returncode != 0:
        logging.info(result.stderr)
        logging.info(result.stdout)
        raise RuntimeError(f'dsub failed. Retcode: {result.returncode}')

    # We need to add more sophisticated job monitoring so KFP GUI is more up to date.

    


    
    