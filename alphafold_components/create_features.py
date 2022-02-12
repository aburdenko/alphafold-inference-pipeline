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
"""A encapsulating AlphaFold feature engineering"""

import os
import logging
import numpy as np
from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union


from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data import templates
from alphafold.data.tools import hhblits
from alphafold.data.tools import hhsearch
from alphafold.data.tools import hmmsearch
from alphafold.data.tools import jackhmmer

from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset


_COMPONENTS_IMAGE = os.getenv('COMPONENTS_IMAGE', 'gcr.io/jk-mlops-dev/alphafold-components')

FeatureDict = MutableMapping[str, np.ndarray]
TemplateSearcher = Union[hhsearch.HHSearch, hmmsearch.Hmmsearch]


@dsl.component(
    base_image=_COMPONENTS_IMAGE,
    output_component_file='component_create_features.yaml'
)
def create_features(
    sequence_input: Input[Dataset],
    msa_input1: Input[Dataset],
    msa_input2: Optional[Input[Dataset]],
    msa_input3: Optional[Input[Dataset]],
    template_input: Input[Dataset],
    features: Output[Dataset]):
    """ Creates features from results of searches against sequence databases.
    
    In the prototype, we assume a fixed number of inputs, mirroring the sample
    inference pipeline from DeepMind. When it comes to productionizing we should
    consider "dynamic" at runtime or at least highly configurable at compile time
    component.

    """

    def _make_sequence_features(
        sequence: str, description: str, num_res: int) -> FeatureDict:
        """Constructs a feature dict of sequence features."""
        features = {}
        features['aatype'] = residue_constants.sequence_to_onehot(
            sequence=sequence,
            mapping=residue_constants.restype_order_with_x,
            map_unknown_to_x=True)
        features['between_segment_residues'] = np.zeros((num_res,), dtype=np.int32)
        features['domain_name'] = np.array([description.encode('utf-8')],
                                        dtype=np.object_)
        features['residue_index'] = np.array(range(num_res), dtype=np.int32)
        features['seq_length'] = np.array([num_res] * num_res, dtype=np.int32)
        features['sequence'] = np.array([sequence.encode('utf-8')], dtype=np.object_)
        return features
        
        
    def _make_msa_features(msas: Sequence[parsers.Msa]) -> FeatureDict:
        """Constructs a feature dict of MSA features."""
        if not msas:
            raise ValueError('At least one MSA must be provided.')

        int_msa = []
        deletion_matrix = []
        uniprot_accession_ids = []
        species_ids = []
        seen_sequences = set()
        for msa_index, msa in enumerate(msas):
            if not msa:
                raise ValueError(f'MSA {msa_index} must contain at least one sequence.')
            for sequence_index, sequence in enumerate(msa.sequences):
                if sequence in seen_sequences:
                    continue
                seen_sequences.add(sequence)
                int_msa.append(
                    [residue_constants.HHBLITS_AA_TO_ID[res] for res in sequence])
                deletion_matrix.append(msa.deletion_matrix[sequence_index])
                identifiers = msa_identifiers.get_identifiers(
                    msa.descriptions[sequence_index])
                uniprot_accession_ids.append(
                    identifiers.uniprot_accession_id.encode('utf-8'))
                species_ids.append(identifiers.species_id.encode('utf-8'))

        num_res = len(msas[0].sequences[0])
        num_alignments = len(int_msa)
        features = {}
        features['deletion_matrix_int'] = np.array(deletion_matrix, dtype=np.int32)
        features['msa'] = np.array(int_msa, dtype=np.int32)
        features['num_alignments'] = np.array(
            [num_alignments] * num_res, dtype=np.int32)
        features['msa_uniprot_accession_identifiers'] = np.array(
            uniprot_accession_ids, dtype=np.object_)
        features['msa_species_identifiers'] = np.array(species_ids, dtype=np.object_)
        return features


    def _read_msa(msa_dataset: Input[Dataset]):
        msa = None
        msa_path = msa_dataset.path,
        msa_format = msa_dataset.metadata['data_format']
        if os.path.exists(msa_path):
            with open(msa_path) as f:
                msa = f.read()
            if msa_format == 'sto':
                msa = parsers.parse_stockholm(msa)
            elif msa_format == 'a3m':
                msa = parsers.parse_a3m(msa)
            else:
                raise RuntimeError(f'Unsupported MSA format: {msa_format}') 
        return msa

    def _read_sequence(sequence_dataset: Input[Dataset])

        sequence_path = sequence_dataset.path
        sequence_format = sequence_dataset.metadata['data_format']

        if sequence_format != 'fasts':
            raise RuntimeError(f'Unsupported sequence format {sequence_format}')

        with open(sequence_path) as f:
            sequence_str = f.read()
        sequences, sequence_descs = parsers.parse_fasta(sequence_str)
        if len(sequences) != 1:
            raise ValueError(
                f'More than one input sequence found in {sequence_path}.')

        return sequences[0], sequence_descs[0], len(sequences[0]

    # Create sequence features
   seq, seq_desc, num_res = _read_sequence(sequence_input) 
   sequence_features = _make_sequence_features(
       sequence=seq,
       description=seq_desc,
       num_res=num_res
   )

    # Create MSA features
    msas = []
    msas.append(_read_msa(msa_input1))
    msas.append(_read_msa(msa_input2))
    msas.append(_read_msa(msa_input3))
    if not msas:
        raise RuntimeError('No MSAs passed to the component')
    msa_features = _make_msa_features(msas=msas)



     
     