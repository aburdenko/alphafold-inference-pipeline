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

"""A script for searching sequence databases using hhblits."""

import logging
import os
import numpy as np
import shutil
import sys

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union

from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data import templates
from alphafold.data.tools import hhblits
from alphafold.data.tools import jackhmmer


_OUTPUT_FILE_PREFIX = 'OUTPUT'

MSA_TOOL = os.environ['MSA_TOOL']
FASTA_PATH = os.environ['FASTA_PATH']
OUTPUT_DIR = os.environ['OUTPUT_DIR']
DATABASE_PATHS = os.environ['DATABASE_PATHS']
N_CPU = int(os.getenv('N_CPU', '2'))
MAX_STO_SEQEUNCES = int(os.getenv('MAX_STO_SEQUENCES', 501))
HHBLITS_BINARY_PATH = shutil.which('hhblits')
JACKHMMER_BINARY_PATH = shutil.which('jackhmmer')


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


def _read_and_check_fasta(fasta_path):
    with open(fasta_path) as f:
        input_fasta_str = f.read()
    input_seqs, input_descs = parsers.parse_fasta(input_fasta_str)
    if len(input_seqs) != 1:
      raise ValueError(
          f'More than one input sequence found in {fasta_path}.')

    return input_seqs, input_descs

def run_hhblits(
    input_fasta_path: str,
    database_paths: Sequence[str],
    n_cpu: int,
    output_dir: str): 
    """Runs hhblits and saves results to a file."""

    runner = hhblits.HHBlits(
        binary_path=HHBLITS_BINARY_PATH,
        databases=database_paths,
        n_cpu=n_cpu
    )

    _, input_desc = _read_and_check_fasta(input_fasta_path)
    logging.info(f'Searching using input sequence: {input_desc}')

    msa_format = 'a3m'
    msa_out_path = os.path.join(output_dir, f'{_OUTPUT_FILE_PREFIX}.{msa_format}')
    result = _run_msa_tool(
        msa_runner=runner,
        input_fasta_path=input_fasta_path,
        msa_out_path=msa_out_path,
        msa_format=msa_format
    )


def run_jackhmmer(
    input_fasta_path: str,
    database_path: str,
    n_cpu: int,
    max_sto_sequences: int,
    output_dir: str): 
    """Runs jackhmeer and saves results to a file."""

    runner = jackhmmer.Jackhmmer(
        binary_path=JACKHMMER_BINARY_PATH,
        database_path=database_path,
        n_cpu=n_cpu,
    )

    _, input_desc = _read_and_check_fasta(input_fasta_path)
    logging.info(f'Searching using input sequence: {input_desc}')

    msa_format = 'sto'
    msa_out_path = os.path.join(output_dir, f'{_OUTPUT_FILE_PREFIX}.{msa_format}')
    result = _run_msa_tool(
        msa_runner=runner,
        input_fasta_path=input_fasta_path,
        msa_out_path=msa_out_path,
        msa_format=msa_format
    )


if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    if MSA_TOOL == 'jackhmmer':
        database_path = DATABASE_PATHS.split(',')[0]
        run_jackhmmer(
            input_fasta_path=FASTA_PATH,
            database_path=database_path,
            n_cpu=N_CPU,
            max_sto_sequences=MAX_STO_SEQEUNCES,
            output_dir=OUTPUT_DIR
        )
    elif MSA_TOOL == 'hhblits':
        run_hhblits(
            input_fasta_path=FASTA_PATH,
            database_paths=DATABASE_PATHS.split(','),
            n_cpu=N_CPU,
            output_dir=OUTPUT_DIR
        )
    else:
      raise ValueError(
          f'Unsupported tool {MSA_TOOL}.')


