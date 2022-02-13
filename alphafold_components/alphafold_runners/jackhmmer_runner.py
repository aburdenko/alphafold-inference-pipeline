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

"""Jackhmmer runner."""

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
from alphafold.data.tools import jackhmmer


# Required inputs
INPUT_PATH= os.environ['INPUT_PATH']
OUTPUT_PATH = os.environ['OUTPUT_PATH']

DB_ROOT = os.environ['DB_ROOT']
DB_PATH = os.environ['DB_PATH']

# Optional inputs 
N_CPU = int(os.getenv('N_CPU'))
MAXSEQ = int(os.getenv('MAXSEQ', '10_000'))

# Paths to tool binaries
JACKHMMER_BINARY_PATH = shutil.which('jackhmmer')


def _read_and_check_fasta(fasta_path):
    with open(fasta_path) as f:
        input_fasta_str = f.read()
    input_seqs, input_descs = parsers.parse_fasta(input_fasta_str)
    if len(input_seqs) != 1:
      raise ValueError(
          f'More than one input sequence found in {fasta_path}.')

    return input_seqs, input_descs


def run_jackhmmer(
    input_path: str,
    output_path: str,
    database_path: str,
    maxseq: int,
    n_cpu: int):
    """Runs jackhmeer and saves results to a file."""

    runner = jackhmmer.Jackhmmer(
        binary_path=JACKHMMER_BINARY_PATH,
        database_path=database_path,
        n_cpu=n_cpu,
    )

    _, input_desc = _read_and_check_fasta(input_path)
    logging.info(f'Searching using input sequence: {input_desc}')
    results = runner.query(input_path, maxseq)[0]
    with open(output_path, 'w') as f: 
        f.write(results['sto'])


if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    database_path = os.path.join(DB_ROOT, DB_PATH)
    run_jackhmmer(
        input_path=INPUT_PATH,
        output_path=OUTPUT_PATH,
        database_path=database_path,
        maxseq=MAXSEQ,
        n_cpu=N_CPU,)
