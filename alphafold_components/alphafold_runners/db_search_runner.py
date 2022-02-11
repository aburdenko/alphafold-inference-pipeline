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
import pathlib
import numpy as np
import shutil
import sys
import time

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union

from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data import templates
from alphafold.data.tools import hhblits
from alphafold.data.tools import jackhmmer
from alphafold.data.tools import hhsearch 


# Required inputs
DB_TOOL = os.environ['DB_TOOL']
INPUT_DATA = os.environ['INPUT_DATA']
INPUT_DATA_FORMAT = os.environ['INPUT_DATA_FORMAT']
OUTPUT_DATA = os.environ['OUTPUT_DATA']
OUTPUT_DATA_FORMAT = os.environ['OUTPUT_DATA_FORMAT']
DATABASE_PATHS = os.environ['DATABASE_PATHS']

# Tools specific inputs
N_CPU = int(os.getenv('N_CPU'))
MAX_STO_SEQEUNCES = int(os.getenv('MAX_STO_SEQUENCES', '10_000'))
MAXSEQ = int(os.getenv('MAXSEQ', '1_000_000'))

# Paths to tool binaries
HHBLITS_BINARY_PATH = shutil.which('hhblits')
JACKHMMER_BINARY_PATH = shutil.which('jackhmmer')
HHSEARCH_BINARY_PATH = shutil.which('hhsearch')


def _run_msa_tool(msa_runner, input_fasta_path: str, msa_out_path: str,
                 msa_format: str, use_precomputed_msas: bool=False,
                 max_sto_sequences: Optional[int] = None
                 ) -> Mapping[str, Any]:
    """Runs an MSA tool, checking if output already exists first."""
    if not use_precomputed_msas or not os.path.exists(msa_out_path):
        if msa_format == 'sto' and max_sto_sequences is not None:
            result = msa_runner.query(input_fasta_path, max_sto_sequences)[0]  # pytype: disable=wrong-arg-count
        else:
            result = msa_runner.query(input_fasta_path)[0]
        logging.info(f"Saving results to {msa_out_path}")
        with open(msa_out_path, 'w') as f:
            f.write(result[msa_format])
    else:
        logging.warning('Reading MSA from file %s', msa_out_path)
        if msa_format == 'sto' and max_sto_sequences is not None:
            precomputed_msa = parsers.truncate_stockholm_msa(
                    msa_out_path, max_sto_sequences)
            result = {'sto': precomputed_msa}
        else:
            with open(msa_out_path, 'r') as f:
                result = {msa_format: f.read()}
    return result


def _save_results(results: str, output_path: str):
    logging.info(f'Saving results to: {output_path'})
    with open(output_path, 'w') as f: 
        f.write(results)


def _read_and_check_fasta(fasta_path):
    with open(fasta_path) as f:
        input_fasta_str = f.read()
    input_seqs, input_descs = parsers.parse_fasta(input_fasta_str)
    if len(input_seqs) != 1:
      raise ValueError(
          f'More than one input sequence found in {fasta_path}.')

    return input_seqs, input_descs


def run_hhblits(
    input_path: str,
    input_format: str,
    output_path: str,
    output_format: str,
    database_paths: Sequence[str],
    n_cpu: int): 
    """Runs hhblits and saves results to a file."""

    if input_format != 'fasta':
        raise ValueError(f'hhblits does not support inputs in {input_format} format')
    if output_format != 'a3m':
        raise ValueError(f'hhblits does not support outputs in {output_format} format')  

    runner = hhblits.HHBlits(
        binary_path=HHBLITS_BINARY_PATH,
        databases=database_paths,
        n_cpu=n_cpu
    )

    _, input_desc = _read_and_check_fasta(input_path)
    logging.info(f'Searching using input sequence: {input_desc}')
    results = runner.query(input_path)
    _save_results(results[0], output_path)


def run_jackhmmer(
    input_path: str,
    input_format: str,
    output_path: str,
    output_format: str,
    database_path: str,
    n_cpu: int,
    max_sto_sequences: int):
    """Runs jackhmeer and saves results to a file."""

    if input_format != 'fasta':
        raise ValueError(f'jackhmmer does not support inputs in {input_format} format')
    if output_format != 'sto':
        raise ValueError(f'jackhmmer does not support outputs in {output_format} format')  

    runner = jackhmmer.Jackhmmer(
        binary_path=JACKHMMER_BINARY_PATH,
        database_path=database_path,
        n_cpu=n_cpu,
    )

    _, input_desc = _read_and_check_fasta(input_path)
    logging.info(f'Searching using input sequence: {input_desc}')
    results = runner.query(input_path, max_sto_sequences)
    _save_results(results[0], output_path)


def run_hhsearch(
    input_path: str,
    input_format: str,
    output_path: str,
    output_format: str,
    database_paths: Sequence[str],
    maxseq: int):
    """Runs hhsearch and saves results to a file."""

    template_format = pathlib.Path(output_path).suffix[1:]
    if template_format != 'hhr':
        raise ValueError(f'hhsearch does not support generating files in {template_format} format') 
    
    if input_format != 'sto' or input_format != 'a3m':
        raise ValueError(f'hhsearch does not support inputs in {input_format} format')
    if output_format != 'hhr':
        raise ValueError(f'hhsearch does not support outputs in {output_format} format')  

    runner = hhsearch.HHSearch(
        binary_path=HHSEARCH_BINARY_PATH,
        databases=database_paths,
        maxseq=maxseq,
    )

    with open(input_path) as f:
        input_msa_str = f.read()

    if  input_format == 'sto':
        msa_for_templates = parsers.deduplicate_stockholm_msa(input_msa_str)
        msa_for_templates = parsers.remove_empty_columns_from_stockholm_msa(msa_for_templates)
        msa_for_templates = parsers.convert_stockholm_to_a3m(msa_for_templates)
    else input_format == 'a3m':
        # TBD - research what kind of preprocessing required for a3m - if any 
        pass

    results = runner.query(msa_for_templates)
    _save_results(results[0], output_path)
 

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    database_paths = DATABASE_PATHS.split(',') 

    if DB_TOOL == 'jackhmmer':
        run_jackhmmer(
            input_path=INPUT_DATA,
            input_data_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_data_format=OUTPUT_DATA_FORMAT,
            database_path=database_paths[0],
            n_cpu=N_CPU,
            max_sto_sequences=MAX_STO_SEQEUNCES,
        )
    elif DB_TOOL == 'hhblits':
        run_hhblits(
            input_path=INPUT_DATA,
            input_data_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_data_format=OUTPUT_DATA_FORMAT,
            database_paths=database_paths,
            n_cpu=N_CPU,
        )
    elif DB_TOOL == 'hhsearch':
        run_hhsearch(
            input_path=INPUT_DATA,
            input_data_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_data_format=OUTPUT_DATA_FORMAT,
            database_paths=database_paths,
            maxseq=MAXSEQ,
        )
    else:
      raise ValueError(
          f'Unsupported tool {DB_TOOL}.')


