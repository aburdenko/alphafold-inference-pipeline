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
"""A component encapsulating AlphaFold model predict"""


from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset
from typing import List

import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE,
    output_component_file='component_import_sequence.yaml'
)
def import_sequence(
    sequence_path: str,
    sequence: Output[Dataset],
):
    from alphafold.data import parsers
    from google.cloud import storage

    client = storage.Client()
    with open(sequence.path, 'wb') as f:
        client.download_blob_to_file(sequence_path, f)

    with open(sequence.path) as f:
        sequence_str = f.read()
    seqs, seq_descs = parsers.parse_fasta(sequence_str)

    if len(seqs) !=1:
        raise ValueError(f'More than one sequence found in {sequence_path}. Unsupported')

    sequence.metadata['sequence']=seqs[0]
    sequence.metadata['description']=seq_descs[0]
    sequence.metadata['data_format']='fasta'
    sequence.metadata['number of residues']=len(seqs[0])
    




    






