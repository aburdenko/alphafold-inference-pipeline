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

_REFERENCE_DATASETS_IMAGE = "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
_UNIREF_PATH = 'uniref90/uniref90.fasta'
_MGNIFY_PATH = 'mgnify/mgy_clusters_2018_12.fa'
_BFD__UNICLUST_PATH = 'uniclust30/uniclust30_2018_08/uniclust30_2018_08,bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'
_PDB_PATH = 'pdb70/pdb70'
_JACKHMMER = 'jackhmmer'
_HHSEARCH = 'hhsearch'
_HHBLITS = 'hhblits'

@dsl.pipeline(name=_PIPELINE_NAME, description=_PIPELINE_DESCRIPTION)
def pipeline(
    fasta_path: str,
    project: str='jk-mlops-dev',
    region: str='us-central1',
    datasets_disk_image: str=_REFERENCE_DATASETS_IMAGE):
    """Runs AlphaFold inference."""

    search_uniref = alphafold_components.DBSearchOp(
        project=project,
        region=region,
        datasets_disk_image=datasets_disk_image,
        database_paths=_UNIREF_PATH,
        input_path=fasta_path,
        search_tool=_JACKHMMER
    )
    search_uniref.set_display_name('Search Uniref')

    search_mgnify = alphafold_components.DBSearchOp(
        project=project,
        region=region,
        datasets_disk_image=datasets_disk_image,
        database_paths=_MGNIFY_PATH,
        input_path=fasta_path,
        search_tool=_JACKHMMER
    )
    search_mgnify.set_display_name('Search Mgnify')

    search_bfd_uniclust = alphafold_components.DBSearchOp(
        project=project,
        region=region,
        datasets_disk_image=datasets_disk_image,
        database_paths=_BFD__UNICLUST_PATH,
        input_path=fasta_path,
        search_tool=_HHBLITS
    )
    search_bfd_uniclust.set_display_name('Search Uniclust and BFD')

    search_pdb = alphafold_components.DBSearchOp(
        project=project,
        region=region,
        datasets_disk_image=datasets_disk_image,
        database_paths=_PDB_PATH,
        input_path=search_uniref.outputs['Output'],
        search_tool=_HHSEARCH
    )
    search_pdb.set_display_name('Search Pdb') 

    


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{_PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

