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
import pickle
import haiku as hk
import time

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union

from alphafold.common import residue_constants
from alphafold.data import msa_identifiers
from alphafold.data import parsers
from alphafold.data.tools import jackhmmer


# Required inputs
DB_ROOT = os.environ['DB_ROOT']
PARAMS_PATH = os.environ['PARAMS_PATH']
MSA_PATHS= os.environ['MSA_PATHS']
SEQUENCE_PATH = os.environ['SEQUENCE_PATH']
TEMPLATES_PATH = os.environ['TEMPLATES_PATH']
MODEL_NAME = os.environ['MODEL_NAME']

OUTPUT_DIR = os.environ['OUTPUT_DIR']

# Optional inputs
NUM_ENSEMBLE = int(os.getenv('NUM_ENSEMBLE', '1')) 
RANDOM_SEED = int(os.getenv('RANDOM_SEED', '0'))
RELAX = int(os.getenv('RELAX', '1'))


def aggregate_features(
    msa_paths: Sequence[str],
    templates_path: str,
    sequence_path: str    
) -> Mapping: 
    pass


def predict_relax(
    features_path: str,
    params_path: str,
    model_name: str,
    num_ensemble: int,
    random_seed: int,
    output_dir: str,
) -> Mapping:
    pass

def main(
    msa_paths: Sequence[str],
    

):
    pass


if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    # Do something more intelligent with random seed
    random_seed = RANDOM_SEED
    if not random_seed:
        random_seed = int(MODEL_NAME[-1])
    
    print(random_seed)


    main(
        features_path=FEATURES_PATH,
        params_path=os.path.join(DB_ROOT, PARAMS_PATH),
        model_name=MODEL_NAME,
        num_ensemble=NUM_ENSEMBLE,
        random_seed=random_seed,
        output_dir=OUTPUT_DIR)
