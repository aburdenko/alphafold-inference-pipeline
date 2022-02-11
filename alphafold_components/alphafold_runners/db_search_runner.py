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

DB_ROOT = os.environ['DB_ROOT']
DB_PATHS = os.environ['DB_PATHS']

# Optional inputs 
N_CPU = int(os.getenv('N_CPU'))
MAXSEQ = int(os.getenv('MAXSEQ', '10_000'))

# Paths to tool binaries
HHBLITS_BINARY_PATH = shutil.which('hhblits')
JACKHMMER_BINARY_PATH = shutil.which('jackhmmer')
HHSEARCH_BINARY_PATH = shutil.which('hhsearch')


def _save_results(results: str, output_path: str, output_format: str):
    """Save results. output_format may be used in future to add a
    proper file name if required."""
    logging.info(f'Saving results to: {output_path}')
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
    n_cpu: int,
    maxseq: int): 
    """Runs hhblits and saves results to a file."""

    if input_format != 'fasta':
        raise ValueError(f'hhblits does not support inputs in {input_format} format')
    if output_format != 'a3m':
        raise ValueError(f'hhblits does not support outputs in {output_format} format')  

    runner = hhblits.HHBlits(
        binary_path=HHBLITS_BINARY_PATH,
        databases=database_paths,
        n_cpu=n_cpu,
        maxseq=maxseq,
    )

    _, input_desc = _read_and_check_fasta(input_path)
    logging.info(f'Searching using input sequence: {input_desc}')
    results = runner.query(input_path)
    _save_results(results[0][output_format], output_path, output_format)


def run_jackhmmer(
    input_path: str,
    input_format: str,
    output_path: str,
    output_format: str,
    database_path: str,
    maxseq: int,
    n_cpu: int):
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
    results = runner.query(input_path, maxseq)
    _save_results(results[0][output_format], output_path, output_format)


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
    elif input_format == 'a3m':
        # TBD - research what kind of preprocessing required for a3m - if any 
        pass

    results = runner.query(msa_for_templates)
    _save_results(results, output_path, output_format)
 

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    database_paths = [
            os.path.join(DB_ROOT, database_path) 
            for database_path in DB_PATHS.split(',')] 

    if DB_TOOL == 'jackhmmer':
        run_jackhmmer(
            input_path=INPUT_DATA,
            input_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_format=OUTPUT_DATA_FORMAT,
            database_path=database_paths[0],
            maxseq=MAXSEQ,
            n_cpu=N_CPU,
        )
    elif DB_TOOL == 'hhblits':
        run_hhblits(
            input_path=INPUT_DATA,
            input_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_format=OUTPUT_DATA_FORMAT,
            database_paths=database_paths,
            maxseq=MAXSEQ,
            n_cpu=N_CPU,
        )
    elif DB_TOOL == 'hhsearch':
        run_hhsearch(
            input_path=INPUT_DATA,
            input_format=INPUT_DATA_FORMAT,
            output_path=OUTPUT_DATA,
            output_format=OUTPUT_DATA_FORMAT,
            database_paths=database_paths,
            maxseq=MAXSEQ,
        )
    else:
      raise ValueError(
          f'Unsupported tool {DB_TOOL}.')


