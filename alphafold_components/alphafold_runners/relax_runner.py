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

"""Predict runner."""

import logging
import os
import sys

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union, Tuple

from alphafold.common import protein
from alphafold.relax import relax


def relax_protein(
    unrelaxed_protein_path: str,
    max_iterations: int=0,
    tolerance: float=2.39,
    stiffness: float=10.0,
    exclude_residues: list=[],
    max_outer_iterations: int=3,
    use_gpu=False
) -> Mapping:

    with open(unrelaxed_protein_path, 'r') as f:
        unrelaxed_protein_pdb=f.read();

    unrelaxed_structure = protein.from_pdb_string(unrelaxed_protein_pdb)
    amber_relaxer = relax.AmberRelaxation(
        max_iterations=max_iterations,
        tolerance=tolerance,
        stiffness=stiffness,
        exclude_residues=exclude_residues,
        max_outer_iterations=max_outer_iterations,
        use_gpu=use_gpu)
    relaxed_protein_pdb, _, _ = amber_relaxer.process(prot=unrelaxed_structure)

    return relaxed_protein_pdb


def _main(
    unrelaxed_protein_path: str,
    relaxed_protein_path: str,
    use_gpu=False
):
    logging.info(f'Starting protein relaxation')
    relaxed_protein_pdb = relax_protein(
        unrelaxed_protein_path=unrelaxed_protein_path,
        use_gpu=use_gpu
    )
 
    logging.info(f'Saving relaxed protein to {relaxed_protein_path}')
    with open(relaxed_protein_path, 'w') as f:
        f.write(relaxed_protein_pdb)
     

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    _main(
        unrelaxed_protein_path=os.environ['UNRELAXED_PROTEIN_PATH'],
        relaxed_protein_path=os.environ['RELAXED_PROTEIN_PATH'],
        use_gpu=bool(os.environ['RELAX_USE_GPU']),
    )