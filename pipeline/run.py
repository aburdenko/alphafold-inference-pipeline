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
import random
from re import I
import sys

from absl import flags
from absl import app

import google.cloud.aiplatform as aip


_PIPELINE_JOB_NAME = 'alphafold-inference'

FLAGS = flags.FLAGS

flags.DEFINE_string('pipeline_spec', 'alphafold-inference.json', 'Path to pipeline spec')
flags.DEFINE_string('pipeline_staging_location', 'gs://alphafold_protein_structure/pipelines', 'Vertex AI staging bucket')
flags.DEFINE_string('dsub_logging_path', 'gs://alphafold_protein_structure/logging', 'dsub logging')
flags.DEFINE_string('project', 'aburdenko-project', 'GCP Project')
flags.DEFINE_string('project_number', '653488387759', 'Project number')
flags.DEFINE_string('region', 'us-central1', 'GCP Region')
flags.DEFINE_string('fasta_path', 'gs://alphafold_protein_structure/upload/sequences.fasta', 'A path to a sequence')
#flags.DEFINE_string('fasta_path', 'gs://jk-alphafold-datasets-archive/fasta/T1050.fasta', 'A path to a sequence')
flags.DEFINE_string('vertex_sa', 'aburdenko-jupyter-notebook@aburdenko-project.iam.gserviceaccount.com', 'Vertex SA')
flags.DEFINE_string('pipelines_sa', 'aburdenko-jupyter-notebook@aburdenko-project.iam.gserviceaccount.com', 'Pipelines SA')
flags.DEFINE_string('uniref90_database_path', 'test1', 'Database paths')
flags.DEFINE_string('databases_disk_image', 'http://test.com', 'Disk image prepopulated with databases')
flags.DEFINE_string('max_template_date', '2020-05-14', 'Max template date')
flags.DEFINE_integer('num_ensemble', 1, 'TBD')
flags.DEFINE_integer('random_seed', None, 'TBD')
flags.DEFINE_bool('enable_caching', True, 'Enable pipeline run caching')
flags.DEFINE_bool('use_gpu_for_relaxation', True, 'Use GPU for relaxation')
flags.DEFINE_string('sequence_desc', 'T1050 A7LXT1, Bacteroides Ovatus, 779 residues', '')

def _main(argv):

    # Think about a better way of dealing with random seeds

    models = [
        {
            'model_name': 'model_1', 'random_seed': 1,
        },
    #    {
    #        'model_name': 'model_2', 'random_seed': 2,
    #    },
    #    {
    #        'model_name': 'model_3', 'random_seed': 3,
    #    },
    #            {
    #        'model_name': 'model_4', 'random_seed': 4,
    #    },
    #            {
    #        'model_name': 'model_5', 'random_seed': 5,
    #    },

    ]
    

    

    params = {
        'sequence_path': FLAGS.fasta_path,
        'sequence_desc': FLAGS.sequence_desc,
        'max_template_date': FLAGS.max_template_date,
        'project': FLAGS.project,
        'region': FLAGS.region,
        'models': models,
        'num_ensemble': FLAGS.num_ensemble,
        'use_gpu_for_relaxation': True,
    }

    pipeline_job = aip.PipelineJob(
        display_name=_PIPELINE_JOB_NAME,
        template_path=FLAGS.pipeline_spec,
        pipeline_root=f'{FLAGS.pipeline_staging_location}/{_PIPELINE_JOB_NAME}',
        parameter_values=params,
        enable_caching=FLAGS.enable_caching,

    )

    pipeline_job.run(
        service_account=FLAGS.pipelines_sa
        
    )


if __name__ == "__main__":
    app.run(_main)
