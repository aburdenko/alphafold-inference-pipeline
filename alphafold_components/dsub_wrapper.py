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
    dstat_cmd = [
        _DSTAT_BINARY_PATH,
        '--provider', provider]
    if provider == 'google-cls-v2':
        google_provider_params = [
        '--project', project,
        '--regions', regions]
        dsub_cmd += google_provider_params
        dstat_cmd += google_provider_params
        
    result = subprocess.run(
        dsub_cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    if result.returncode != 0:
        logging.info(result.stderr)
        logging.info(result.stdout)
        raise RuntimeError(f'dsub failed to launch the job. Retcode: {result.returncode}')

    logging.info('Waiting for the job to complete') 
    dstat_cmd += ['--jobs', result.stdout.decode('UTF-8').strip()]
    dstat_cmd.append('--wait')
    result = subprocess.run(
        dstat_cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    #while True:
    #    result = subprocess.run(
    #        dstat_cmd,
    #        stderr=subprocess.PIPE,
    #        stdout=subprocess.PIPE)

    #    if result.stdout.decode('UTF-8').strip() == "":
    #        break

    #    # Logging must dramatically improve :)
    #    logging.info(result.stdout) 
    #    time.sleep(_POLLING_INTERVAL)


    return result


    
    