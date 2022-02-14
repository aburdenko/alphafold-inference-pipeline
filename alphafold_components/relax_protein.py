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

import io
import numpy as np
import os

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union
from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset
from typing import List

_COMPONENTS_IMAGE = os.getenv('COMPONENTS_IMAGE', 'gcr.io/jk-mlops-dev/alphafold')


@dsl.component(
    base_image=_COMPONENTS_IMAGE,
    output_component_file='component_relax.yaml'
)
def relax(
    unrelaxed_protein: Input[Artifact],
    relaxed_protein: Output[Artifact],
    max_iterations: int=0,
    tolerance: float=2.39,
    stiffness: float=10.0,
    exclude_residues: list=[],
    max_outer_iterations: int=3,
    use_gpu: bool=True,
):
    
    import os
    import logging
    import numpy as np
    import pickle

    from alphafold.model import utils
    from alphafold.common import residue_constants
    from alphafold.common import protein
    from alphafold.relax import relax


    if not os.path.exists(unrelaxed_protein.path):
        raise RuntimeError(f'Invalid path to unrelaxed structure: {unrelaxed_protein.path}')
    
    with open(unrelaxed_protein.path, 'r') as f:
        unrelaxed_protein_pdb=f.read();

    unrelaxed_protein = protein.from_pdb_string(unrelaxed_protein_pdb)
    
    amber_relaxer = relax.AmberRelaxation(
        max_iterations=max_iterations,
        tolerance=tolerance,
        stiffness=stiffness,
        exclude_residues=exclude_residues,
        max_outer_iterations=max_outer_iterations,
        use_gpu=use_gpu)

    relaxed_protein = amber_relaxer.process(prot=unrelaxed_protein)
    
    relaxed_protein_pdb = protein.to_pdb(relaxed_protein) 
    with open(relaxed_protein.path, 'w') as f:
        f.write(relaxed_protein_pdb)
    relaxed_protein.metadata['data_format']='pdb'






