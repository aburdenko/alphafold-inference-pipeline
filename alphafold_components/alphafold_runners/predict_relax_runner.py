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

import io
import logging
import os
import numpy as np
import sys
import pickle
import haiku as hk
import time

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union, Tuple

from alphafold.model import config
from alphafold.model import model
from alphafold.model import utils
from alphafold.common import residue_constants
from alphafold.common import protein


from predict_runner import predict
from relax_runner import relax_protein

def _main(
    model_features_path: str,
    model_params_path: str,
    model_name: str,
    num_ensemble: int,
    random_seed: int,
    raw_prediction_path: str,
    unrelaxed_protein_path: str,
    relax_after_predict: bool=False,
    relaxed_protein_path: str=None,
    use_gpu_for_relaxation: bool=True,
):
    logging.info(f'Running prediction using model {model_name}')
    prediction_result, unrelaxed_pdbs = predict(
        model_features_path=model_features_path,
        model_params_path=model_params_path,
        model_name=model_name,
        num_ensemble=num_ensemble,
        random_seed=random_seed
    )

    logging.info(f'Writing model {model_name} prediction to {raw_prediction_path}') 
    with open(raw_prediction_path, 'wb') as f:
        pickle.dump(prediction_result, f, protocol=4)

    logging.info(f'Writing unrelaxed protein generated by {model_name} to {unrelaxed_protein_path}') 
    with open(unrelaxed_protein_path, 'w') as f:
        f.write(unrelaxed_pdbs)

    if not relax_after_predict:
        return

    logging.info(f'Starting protein relaxation')
    relaxed_protein_pdb = relax_protein(
        unrelaxed_protein_path=unrelaxed_protein_path,
        use_gpu=use_gpu_for_relaxation,
    )
 
    logging.info(f'Saving relaxed protein to {relaxed_protein_path}')
    with open(relaxed_protein_path, 'w') as f:
        f.write(relaxed_protein_pdb)
     

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    random_seed = int(os.getenv('RANDOM_SEED', '0'))

    # TODO: Do something more intelligent with random seed
    if not random_seed:
        random_seed = int(os.environ['MODEL_NAME'][-1])

    _main(
        model_features_path=os.environ['FEATURES_PATH'],
        model_params_path=os.environ['MODEL_PARAMS_PATH'],
        model_name=os.environ['MODEL_NAME'],
        num_ensemble=int(os.getenv('NUM_ENSEMBE', '1')),
        random_seed=random_seed,
        raw_prediction_path=os.environ['RAW_PREDICTION_PATH'],
        unrelaxed_protein_path=os.environ["UNRELAXED_PROTEIN_PATH"],
        relax_after_predict=bool(os.getenv('RELAX_USE_GPU')),
        relaxed_protein_path=os.getenv('RELAXED_PROTEIN_PATH')
    )