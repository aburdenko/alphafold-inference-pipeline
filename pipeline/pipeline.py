#! /usr/local/bin/python
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
from alphafold_components import  (
    RelaxProteinOp, AggregateFeaturesOp, ModelPredictOp, 
    JackhmmerOp, HHBlitsOp, HHSearchOp, ImportSeqenceOp)


@dsl.pipeline(name=config.PIPELINE_NAME, description=config.PIPELINE_DESCRIPTION)
def pipeline(
    sequence_path: str,
    sequence_desc: str,
    project: str='aburdenk-project',
    region: str='us-central1',
    max_template_date: str='2020-05-14',
    models: List[Mapping]=[{'model_name': 'model_1', 'random_seed': 1}],
    use_gpu_for_relaxation: bool=True,
    num_ensemble: int=1,
    reference_datasets_uri: str=config.REFERENCE_DATASETS_URI, 
    model_params_uri: str=config.MODEL_PARAMS_GCS_LOCATION):
    """Runs AlphaFold inference."""

    input_sequence = dsl.importer(
        artifact_uri=sequence_path,
        artifact_class=dsl.Dataset,
        reimport=True)
    input_sequence.set_display_name('Input sequence')

    model_parameters = dsl.importer(
        artifact_uri=model_params_uri,
        artifact_class=dsl.Artifact,
        reimport=True)
    model_parameters.set_display_name('Model parameters')

    reference_databases = dsl.importer(
        artifact_uri=reference_datasets_uri,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={
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
    search_uniref.set_display_name('Search Uniref')#.set_caching_options(enable_caching=True)

    search_mgnify = JackhmmerOp(
        project=project,
        region=region,
        database=config.MGNIFY,
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_mgnify.set_display_name('Search Mgnify')#.set_caching_options(enable_caching=True)

    search_uniclust = HHBlitsOp(
        project=project,
        region=region,
        msa_dbs=[config.UNICLUST30],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_uniclust.set_display_name('Search Uniclust')#.set_caching_options(enable_caching=True)

    search_bfd = HHBlitsOp(
        project=project,
        region=region,
        msa_dbs=[config.BFD],
        reference_databases=reference_databases.output,
        sequence=input_sequence.output,
    )
    search_bfd.set_display_name('Search BFD')#.set_caching_options(enable_caching=True)

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
    search_pdb.set_display_name('Search Pdb')#.set_caching_options(enable_caching=True)

    aggregate_features = AggregateFeaturesOp(
        sequence=input_sequence.output,
        msa1=search_uniref.outputs['msa'],
        msa2=search_mgnify.outputs['msa'],
        msa3=search_bfd.outputs['msa'],
        msa4=search_uniclust.outputs['msa'],
        template_features=search_pdb.outputs['template_features'],
    )
    aggregate_features.set_display_name('Aggregate features')#.set_caching_options(enable_caching=True)

    # Think what to do with random seed when switch to Parallel loop
    with dsl.ParallelFor(models) as model:
        model_predict = ModelPredictOp(
            model_features=aggregate_features.outputs['features'],
            model_params=model_parameters.output,
            model_name=model.model_name,
            num_ensemble=num_ensemble,
            random_seed=model.random_seed
        )
        model_predict.set_display_name('Predict')#.set_caching_options(enable_caching=True)
        model_predict.set_cpu_limit(config.CPU_LIMIT)
        model_predict.set_memory_limit(config.MEMORY_LIMIT)
        model_predict.set_gpu_limit(config.GPU_LIMIT)
        model_predict.add_node_selector_constraint(config.GKE_ACCELERATOR_KEY, config.GPU_TYPE)
        model_predict.set_env_variable("TF_FORCE_UNIFIED_MEMORY", config.TF_FORCE_UNIFIED_MEMORY)
        model_predict.set_env_variable("XLA_PYTHON_CLIENT_MEM_FRACTION", config.XLA_PYTHON_CLIENT_MEM_FRACTION)

        relax_protein = RelaxProteinOp(
            unrelaxed_protein=model_predict.outputs['unrelaxed_protein'],
            use_gpu=use_gpu_for_relaxation,
        )
        relax_protein.set_display_name('Relax protein')#.set_caching_options(enable_caching=True)
        relax_protein.set_cpu_limit(config.RELAX_CPU_LIMIT)
        relax_protein.set_memory_limit(config.RELAX_MEMORY_LIMIT)
        relax_protein.set_gpu_limit(config.RELAX_GPU_LIMIT)
        relax_protein.add_node_selector_constraint(config.GKE_ACCELERATOR_KEY, config.RELAX_GPU_TYPE)
        relax_protein.set_env_variable("TF_FORCE_UNIFIED_MEMORY", config.TF_FORCE_UNIFIED_MEMORY)
        relax_protein.set_env_variable("XLA_PYTHON_CLIENT_MEM_FRACTION", config.XLA_PYTHON_CLIENT_MEM_FRACTION)
 


def _main(argv):
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=f'{config.PIPELINE_NAME}.json')


if __name__ == "__main__":
    app.run(_main)
    

