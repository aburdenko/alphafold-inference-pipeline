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

from alphafold_components import MSASearchOp, TemplateSearchOp, AggregateFeaturesOp, ModelPredictOp

FLAGS = flags.FLAGS

_PIPELINE_NAME = 'alphafold-inference'
_PIPELINE_DESCRIPTION = 'Alphafold inference'

flags.DEFINE_string('uniref90_database_path', '/uniref90/uniref90.fasta', 'Path to the Uniref90 '
                    'database for use by JackHMMER.')

_REFERENCE_DATASETS_IMAGE = "https://www.googleapis.com/compute/v1/projects/jk-mlops-dev/global/images/jk-alphafold-datasets 3000"
_REFERENCE_DATASETS_GCS_LOCATION = 'gs://jk-alphafold-datasets-archive/jan-22/params'
_MODEL_PARAMS_GCS_LOCATION='gs://'

_UNIREF90_PATH = 'uniref90/uniref90.fasta'
_MGNIFY_PATH = 'mgnify/mgy_clusters_2018_12.fa'
_BFD_PATH = 'bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt'
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
    random_seed: int,
    project: str='jk-mlops-dev',
    region: str='us-central1',
    max_template_date: str='2020-05-14',
    model_name: str='model_1',
    num_ensemble: int=1,
    datasets_gcs_location: str=_REFERENCE_DATASETS_GCS_LOCATION,
    model_params_gcs_location: str=_MODEL_PARAMS_GCS_LOCATION):
    """Runs AlphaFold inference."""

    input_sequence = dsl.importer(
        artifact_uri=fasta_path,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={'data_format': 'fasta'}
    )
    input_sequence.set_display_name('Input sequence')

    model_parameters = dsl.importer(
        artifact_uri=model_params_gcs_location,
        artifact_class=dsl.Artifact,
        reimport=False,
    )

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


    search_uniref = MSASearchOp(
        project=project,
        region=region,
        msa_dbs=[_UNIREF90],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_uniref.set_display_name('Search Uniref').set_caching_options(enable_caching=True)

    search_mgnify = MSASearchOp(
        project=project,
        region=region,
        msa_dbs=[_MGNIFY],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_mgnify.set_display_name('Search Mgnify').set_caching_options(enable_caching=True)

    search_bfd_uniclust = MSASearchOp(
        project=project,
        region=region,
        msa_dbs=[_BFD, _UNICLUST30],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_bfd_uniclust.set_display_name('Search Uniclust and BFD').set_caching_options(enable_caching=True)

    search_pdb = TemplateSearchOp(
        project=project,
        region=region,
        template_dbs=[_PDB70],
        mmcif_db=_PDB_MMCIF,
        obsolete_db=_PDB_OBSOLETE,
        max_template_date=max_template_date,
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
        msa=search_uniref.outputs['msa'],
    )
    search_pdb.set_display_name('Search Pdb').set_caching_options(enable_caching=True)

    aggregate_features = AggregateFeaturesOp(
        sequence=input_sequence.output,
        msa1=search_uniref.outputs['msa'],
        msa2=search_mgnify.outputs['msa'],
        msa3=search_bfd_uniclust.outputs['msa'],
        template_features=search_pdb.outputs['template_features'],
    )
    aggregate_features.set_display_name('Aggregate features').set_caching_options(enable_caching=True)

    # Think what to do with random seed when switch to Parallel loop
    model_predict = ModelPredictOp(
        model_features=aggregate_features.outputs['model_features'],
        model_params=model_parameters.output,
        model_name=model_name,
        num_ensemble=num_ensemble,
        random_seed=random_seed
    )
    model_predict.set_display_name('Predict')


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{_PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

