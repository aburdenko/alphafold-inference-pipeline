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


import logging
import numpy as np
import os
import pathlib
import pickle
import sys

from typing import List

from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data import templates


# Required inputs
SEQUENCE_PATH = os.environ['SEQUENCE_PATH']
MSA_PATHS = os.environ['MSA_PATHS']
TEMPLATE_FEATURES_PATH = os.environ['TEMPLATE_FEATURES_PATH']
OUTPUT_FEATURES_PATH = os.environ['OUTPUT_FEATURES_PATH']


def _make_sequence_features(
    sequence: str, description: str, num_res: int) -> dict:
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


def _make_msa_features(msas: List[parsers.Msa]) -> dict:
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


def _read_msa(msa_path: str, msa_format: str):

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

def _read_sequence(sequence_path: str):

    with open(sequence_path) as f:
        sequence_str = f.read()
    sequences, sequence_descs = parsers.parse_fasta(sequence_str)
    if len(sequences) != 1:
        raise ValueError(
            f'More than one input sequence found in {sequence_path}.')

    return sequences[0], sequence_descs[0], len(sequences[0])


def _read_template_features(template_features_path):
    with open(template_features_path, 'rb') as f:
        template_features = pickle.load(f)
    return template_features


def aggregate_features(
    sequence_path: str,
    msa_paths: List[dict],
    template_features_path: str,
    output_features_path: str):
    """Aggregates MSAs and template features to create model features.""" 

    logging.info('Starting feature aggregation ...')

    # Create sequence features
    seq, seq_desc, num_res = _read_sequence(sequence_path) 
    sequence_features = _make_sequence_features(
        sequence=seq,
        description=seq_desc,
        num_res=num_res)
    
    msas = []
    for msa_path, msa_format in msa_paths.items():
        msas.append(_read_msa(msa_path, msa_format))

    if not msas:
        raise RuntimeError('No MSAs passed to the component')
    msa_features = _make_msa_features(msas=msas)

    # Create template features
    template_features = _read_template_features(template_features_path)
    model_features = {
        ** sequence_features,
        **msa_features,
        **template_features
    }
    with open(output_features_path, 'wb') as f:
        pickle.dump(model_features, f, protocol=4)
    logging.info(f'Feature aggregation completed. Save to {output_features_path}')

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    msa_paths = MSA_PATHS.split(',')
    msa_paths = {msa_path: pathlib.Path(msa_path).suffix[1:] 
                 for msa_path in msa_paths} 

    aggregate_features(
        sequence_path=SEQUENCE_PATH,
        msa_paths=msa_paths,
        template_features_path=TEMPLATE_FEATURES_PATH,
        output_features_path=OUTPUT_FEATURES_PATH)


    



     
     