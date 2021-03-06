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

import os

from typing import Any, Mapping, MutableMapping, Optional, Sequence, Union
from kfp.v2 import dsl
from kfp.v2.dsl import Output, Input, Artifact, Dataset
from typing import List

import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE,
    output_component_file='component_predict.yaml'
)
def predict(
    model_features: Input[Dataset],
    model_params: Input[Artifact],
    model_name: str,
    num_ensemble: int,
    random_seed: int,
    raw_prediction: Output[Artifact],
    unrelaxed_protein: Output[Artifact]
):
    
    import io
    import os
    import logging
    import numpy as np
    import pickle
    import haiku as hk
    import time

    from alphafold.model import config
    from alphafold.model import model
    from alphafold.model import utils
    from alphafold.common import residue_constants
    from alphafold.common import protein

    def _get_model_haiku_params(model_name: str,
                                params_dir: str):
        """Get the Haiku parameters from a model name."""

        path = os.path.join(params_dir, f'params_{model_name}.npz')
        with open(path, 'rb') as f:
            params = np.load(io.BytesIO(f.read()), allow_pickle=False)

        return utils.flat_params_to_haiku(params)

    def _load_features(features_path):
        with open(features_path, 'rb') as f:
            features = pickle.load(f)
        return features


    t0 = time.time()
    logging.info('Starting model predict ...')

    model_config = config.model_config(model_name)

    # we assume  a monomer pipeline in a POC
    model_config.data.eval.num_ensemble = num_ensemble
    model_params = _get_model_haiku_params(
        model_name=model_name, params_dir=model_params.path)
    model_runner = model.RunModel(model_config, model_params)

    features = _load_features(model_features.path)
    logging.info(f'Running prediction using model {model_name}')
    processed_feature_dict = model_runner.process_features(
        raw_features=features,
        random_seed=random_seed
    )
    prediction_result = model_runner.predict(
        feat=processed_feature_dict,
        random_seed=random_seed
    )

    logging.info(f'Writing model {model_name} prediction to {raw_prediction.path}') 
    with open(raw_prediction.path, 'wb') as f:
        pickle.dump(prediction_result, f, protocol=4)
    raw_prediction.metadata['ranking_confidence']=prediction_result['ranking_confidence']
    raw_prediction.metadata['data_format']='pkl'

    plddt = prediction_result['plddt']
    plddt_b_factors = np.repeat(
        plddt[:, None], residue_constants.atom_type_num, axis=-1)
    unrelaxed_structure= protein.from_prediction(
        features=processed_feature_dict,
        result=prediction_result,
        b_factors=plddt_b_factors,
        remove_leading_feature_dimension=not model_runner.multimer_mode)
    unrelaxed_pdbs = protein.to_pdb(unrelaxed_structure)

    logging.info(f'Writing unrelaxed protein generated by {model_name} to {unrelaxed_protein.path}') 
    with open(unrelaxed_protein.path, 'w') as f:
        f.write(unrelaxed_pdbs)
    unrelaxed_protein.metadata['data_format']='pdb'

    t1 = time.time()
    logging.info(f'Model completed. Elapsed time: {t1-t0}')





