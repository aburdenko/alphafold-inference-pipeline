#!/usr/bin/env python
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

"""A script for searching sequence databases."""

import logging
import os
import numpy as np
import pickle
import shutil
import sys

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union

from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data import templates
from alphafold.data.tools import hhsearch 


# Required inputs
INPUT_SEQUENCE_PATH = os.environ['INPUT_SEQUENCE_PATH']
INPUT_MSA_PATH = os.environ['INPUT_MSA_PATH']
MSA_DATA_FORMAT = os.environ['MSA_DATA_FORMAT']
OUTPUT_TEMPLATE_HITS_PATH = os.environ['OUTPUT_TEMPLATE_HITS_PATH']
OUTPUT_TEMPLATE_FEATURES_PATH = os.environ['OUTPUT_TEMPLATE_FEATURES_PATH']
MAX_TEMPLATE_DATE = os.environ['MAX_TEMPLATE_DATE']

DB_ROOT = os.environ['DB_ROOT']
DB_PATHS = os.environ['DB_PATHS']
MMCIF_PATH = os.environ['MMCIF_PATH']
OBSOLETE_PATH = os.environ['OBSOLETE_PATH']

# Optional inputs 
MAXSEQ = int(os.getenv('MAXSEQ', '10_000'))
MAX_TEMPLATE_HITS = int(os.getenv('MAX_TEMPLATE_HITS', 20))

# Paths to tool binaries
HHSEARCH_BINARY_PATH = shutil.which('hhsearch')
KALIGN_BINARY_PATH = shutil.which('kalign')


def _read_and_check_fasta(fasta_path):
    with open(fasta_path) as f:
        input_fasta_str = f.read()
    input_seqs, input_descs = parsers.parse_fasta(input_fasta_str)
    if len(input_seqs) != 1:
      raise ValueError(
          f'More than one input sequence found in {fasta_path}.')

    return input_seqs, input_descs


def run_hhsearch(
    input_sequence_path: str,
    input_msa_path: str,
    msa_data_format: str,
    output_template_hits_path: str,
    output_template_features_path: str,
    database_paths: Sequence[str],
    mmcif_path: str,
    obsolete_path: str,
    max_template_date,
    max_template_hits,
    maxseq: int):
    """Runs hhsearch and saves results to a file."""


    input_sequence, _ = _read_and_check_fasta(input_sequence_path)

    template_searcher = hhsearch.HHSearch(
        binary_path=HHSEARCH_BINARY_PATH,
        databases=database_paths,
        maxseq=maxseq
    )

    template_featurizer = templates.HmmsearchHitFeaturizer(
        mmcif_dir=mmcif_path,
        max_template_date=max_template_date,
        max_hits=max_template_hits,
        kalign_binary_path=KALIGN_BINARY_PATH,
        obsolete_pdbs_path=obsolete_path,
        release_dates_path=None,
    )

    with open(input_msa_path) as f:
        input_msa_str = f.read()

    if  msa_data_format == 'sto':
        msa_for_templates = parsers.deduplicate_stockholm_msa(input_msa_str)
        msa_for_templates = parsers.remove_empty_columns_from_stockholm_msa(msa_for_templates)
        msa_for_templates = parsers.convert_stockholm_to_a3m(msa_for_templates)
    elif msa_data_format == 'a3m':
        # TBD - research what kind of preprocessing required for a3m - if any 
        pass

    templates_result = template_searcher(msa_for_templates)
    with open(output_template_hits_path, 'w') as f:
        f.write(templates_result)

    template_hits = template_searcher.get_template_hits(
        output_string=templates_result, input_sequence=input_sequence)

    templates_result = template_featurizer.get_templates(
        query_sequence=input_sequence,
        hits=template_hits
    )
    
    with open(output_template_features_path, 'w') as f:
        pickle.dump(templates_result.features, f, protocol=4)

    

    



if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    database_paths = [
            os.path.join(DB_ROOT, database_path) 
            for database_path in DB_PATHS.split(',')] 
    mmcif_path = os.path.join(DB_ROOT, MMCIF_PATH)
    obsolete_path = os.path.join(DB_ROOT, OBSOLETE_PATH)

    run_hhsearch(
        input_sequence_path=INPUT_SEQUENCE_PATH,
        input_msa_path=INPUT_MSA_PATH,
        msa_data_format=MSA_DATA_FORMAT,
        output_template_hits_path=OUTPUT_TEMPLATE_HITS_PATH,
        output_template_features_path=OUTPUT_TEMPLATE_FEATURES_PATH,
        database_paths=database_paths,
        mmcif_path=mmcif_path,
        obsolete_path= obsolete_path,
        max_template_date=MAX_TEMPLATE_DATE,
        max_template_hits=MAX_TEMPLATE_HITS,
        maxseq=MAXSEQ)


