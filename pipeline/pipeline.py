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
from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union, List

from kfp.v2 import dsl
from kfp.v2 import compiler
from kfp import components

import config
from alphafold_components import  AggregateFeaturesOp, ModelPredictOp, JackhmmerOp, HHBlitsOp, HHSearchOp


@dsl.pipeline(name=config.PIPELINE_NAME, description=config.PIPELINE_DESCRIPTION)
def pipeline(
    fasta_path: str,
    project: str='jk-mlops-dev',
    region: str='us-central1',
    max_template_date: str='2020-05-14',
    models: List[Mapping]=[{'model_name': 'model_1'}, {'random_seed': 1}],
    num_ensemble: int=1,
    datasets_gcs_location: str=config.REFERENCE_DATASETS_GCS_LOCATION,
    model_params_gcs_location: str=config.MODEL_PARAMS_GCS_LOCATION):
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
        reimport=True,
        metadata={'Description': 'AlphaFold parameters - v2.2'}
    )
    model_parameters.set_display_name('Model parameters')

    reference_databases = dsl.importer(
        artifact_uri=datasets_gcs_location,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={
            'disk_image': config.REFERENCE_DATASETS_IMAGE,
            config.UNIREF90: config.UNIREF90_PATH,
            config.MGNIFY: config.MGNIFY_PATH,
            config.BFD: config.BFD_PATH,
            config.UNICLUST30: config.UNICLUST30_PATH,
            config.PDB70: config.PDB70_PATH,
            config.PDB_MMCIF: config.PDB_MMCIF_PATH,
            config.PDB_OBSOLETE: config.PDB_OBSOLETE_PATH,
            config.PDB_SEQRES: config.PDB_SEQRES_PATH,
            config.UNIPROT: config.UNIPROT_PATH,
            }    
    )
    reference_databases.set_display_name('Reference databases')


    search_uniref = JackhmmerOp(
        project=project,
        region=region,
        database=config.UNIREF90,
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_uniref.set_display_name('Search Uniref').set_caching_options(enable_caching=True)

    search_mgnify = JackhmmerOp(
        project=project,
        region=region,
        database=config.MGNIFY,
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_mgnify.set_display_name('Search Mgnify').set_caching_options(enable_caching=True)

    #search_bfd_uniclust = HHBlitsOp(
    #    project=project,
    #    region=region,
    #    msa_dbs=[config.BFD, config.UNICLUST30],
    #    reference_databases=reference_databases.output,
    #    sequence=input_sequence.output,
    #)
    #search_bfd_uniclust.set_display_name('Search Uniclust and BFD').set_caching_options(enable_caching=True)

    search_uniclust = HHBlitsOp(
        project=project,
        region=region,
        msa_dbs=[config.UNICLUST30],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_uniclust.set_display_name('Search Uniclust').set_caching_options(enable_caching=True)

    search_bfd = HHBlitsOp(
        project=project,
        region=region,
        msa_dbs=[config.BFD],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_bfd.set_display_name('Search BFD').set_caching_options(enable_caching=True)

    search_pdb = HHSearchOp(
        project=project,
        region=region,
        template_dbs=[config.PDB70],
        mmcif_db=config.PDB_MMCIF,
        obsolete_db=config.PDB_OBSOLETE,
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
        msa3=search_bfd.outputs['msa'],
        msa4=search_uniclust.outputs['msa'],
        template_features=search_pdb.outputs['template_features'],
    )
    aggregate_features.set_display_name('Aggregate features').set_caching_options(enable_caching=True)

    # Think what to do with random seed when switch to Parallel loop
    with dsl.ParallelFor(models) as model:
        model_predict = ModelPredictOp(
            model_features=aggregate_features.outputs['model_features'],
            model_params=model_parameters.output,
            model_name=model.name,
            num_ensemble=num_ensemble,
            random_seed=model.random_seed
        )
        model_predict.set_display_name('Predict')
        model_predict.set_cpu_limit(config.CPU_LIMIT)
        model_predict.set_memory_limit(config.MEMORY_LIMIT)
        model_predict.set_gpu_limit(config.GPU_LIMIT)
        model_predict.add_node_selector_constraint(config.GKE_ACCELERATOR_KEY, config.GPU_TYPE)


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{config.PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

