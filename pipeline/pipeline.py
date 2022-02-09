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
import json
from re import I


from absl import flags
from absl import app
from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union

from kfp.v2 import dsl
from kfp.v2 import compiler
from kfp import components

import alphafold_components

FLAGS = flags.FLAGS

_PIPELINE_NAME = 'alphafold-inference'
_PIPELINE_DESCRIPTION = 'Alphafold inference'

flags.DEFINE_string('uniref90_database_path', '/uniref90/uniref90.fasta', 'Path to the Uniref90 '
                    'database for use by JackHMMER.')



@dsl.pipeline(name=_PIPELINE_NAME, description=_PIPELINE_DESCRIPTION)
def pipeline(
    dsub_logging_path: str,
    fasta_path: str,
    databases_disk_image: str,
    uniref90_database_path: list,
    project: str='jk-mlops-dev',
    region: str='us-central1'):
    """Runs AlphaFold inference."""

    #database_paths = json.dumps([str(uniref90_database_path)])
    search_uniref90 = alphafold_components.MSASearchOp(
        search_tool='jackhmmer', 
        database_paths=uniref90_database_path,
        databases_disk_image=databases_disk_image) 


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{_PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

