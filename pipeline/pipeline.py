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

from alphafold_components import DBSearchOp

FLAGS = flags.FLAGS

_PIPELINE_NAME = 'alphafold-inference'
_PIPELINE_DESCRIPTION = 'Alphafold inference'

flags.DEFINE_string('uniref90_database_path', '/uniref90/uniref90.fasta', 'Path to the Uniref90 '
                    'database for use by JackHMMER.')

_REFERENCE_DATASETS_IMAGE = "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
_REFERENCE_DATASETS_GCS_LOCATION = 'gs://jk-alphafold-datasets-archive/jan-22'
_UNIREF90_PATH = 'uniref90/uniref90.fasta'
_MGNIFY_PATH = 'mgnify/mgy_clusters_2018_12.fa'
_BFD_PATH = 'bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'
_UNICLUST30_PATH = 'uniclust30/uniclust30_2018_08/uniclust30_2018_08'
_UNIPROT_PATH = 'uniprot/uniprot.fasta'
_PDB70_PATH = 'pdb70/pdb70'
_PDB_MMCIF = 'pdb_mmcif/mmcif_files'
_PDB_OBSOLETE_PATH = 'pdb_mmcif/obsolete.dat'
_PDB_SEQRES_PATH = 'pdb_seqres/pdb_seqres.txt'

_UNIREF90 = 'uniref90'
_MGNIFY = 'mgnify'
_BFD = 'bfd'
_UNICLUST30 = 'uniclust30'
_PDB70 = 'pdb70'
_PDB_MMCIF = 'pdb_mmcif'
_PDB_OBSOLETE = 'pdb_obsolete'
_PDB_SEQRES = 'pdb_seqres'
_UNIPROT = 'uniprot'

_JACKHMMER = 'jackhmmer'
_HHSEARCH = 'hhsearch'
_HHBLITS = 'hhblits'

@dsl.pipeline(name=_PIPELINE_NAME, description=_PIPELINE_DESCRIPTION)
def pipeline(
    fasta_path: str,
    project: str='jk-mlops-dev',
    region: str='us-central1',
    datasets_disk_image: str=_REFERENCE_DATASETS_IMAGE,
    datasets_gcs_location: str=_REFERENCE_DATASETS_GCS_LOCATION):
    """Runs AlphaFold inference."""

    input_sequence = dsl.importer(
        artifact_uri=fasta_path,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={'data_format': 'fasta'}
    )
    input_sequence.set_display_name('Input sequence')

    reference_databases = dsl.importer(
        artifact_uri=datasets_gcs_location,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={
            'disk_image': _REFERENCE_DATASETS_IMAGE,
            _UNIREF90: _UNIREF90_PATH,
            _MGNIFY: _MGNIFY_PATH,
            _BFD: _BFD_PATH,
            _UNICLUST30: _UNICLUST30_PATH,
            _PDB70: _PDB70_PATH,
            _PDB_MMCIF: _PDB_MMCIF,
            _PDB_OBSOLETE: _PDB_OBSOLETE_PATH,
            _PDB_SEQRES: _PDB_SEQRES_PATH,
            _UNIPROT: _UNIPROT_PATH,
            }    
    )
    reference_databases.set_display_name('Reference databases')


    search_uniref = DBSearchOp(
        project=project,
        region=region,
        database_list=[_UNIREF90],
        reference_databases=reference_databases.output,
        input_data=input_sequence.output,
    )
    search_uniref.set_display_name('Search Uniref').set_caching_options(enable_caching=True)

    search_mgnify = DBSearchOp(
        project=project,
        region=region,
        database_list=[_MGNIFY],
        reference_databases=reference_databases.output,
        input_data=input_sequence.output,
    )
    search_mgnify.set_display_name('Search Mgnify').set_caching_options(enable_caching=True)

    search_bfd_uniclust = DBSearchOp(
        project=project,
        region=region,
        database_list=[_BFD],
        reference_databases=reference_databases.output,
        input_data=input_sequence.output,
    )
    search_bfd_uniclust.set_display_name('Search Uniclust and BFD').set_caching_options(enable_caching=True)

    search_pdb = DBSearchOp(
        project=project,
        region=region,
        database_list=[_PDB70, _UNICLUST30],
        reference_databases=reference_databases.output,
        input_data=search_uniref.outputs['output_data'],
    )
    search_pdb.set_display_name('Search Pdb').set_caching_options(enable_caching=True)


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{_PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

