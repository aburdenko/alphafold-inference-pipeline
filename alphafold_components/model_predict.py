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
    output_component_file='component_predict.yaml'
)
def predict(
    model_features: Input[Dataset],
    model_params: Input[Artifact],
    model_name: str,
    num_ensemble: int,
    random_seed: int,
    prediction_result: Output[Artifact],
    unrelaxed_protein: Output[Artifact]
):
    
    import os
    import logging
    import numpy as np
    import pickle

    import haiku as hk

    from alphafold.model import config
    from alphafold.model import data
    from alphafold.model import model
    from alphafold.model import utils
    from alphafold.common import residue_constants
    from alphafold.common import protein


    def _get_model_haiku_params(model_name: str,
                                model_params: Input[Dataset]):
        """Get the Haiku parameters from a model name."""

        params_dir = model_params.path
        path = os.path.join(params_dir, f'params_{model_name}.npz')

        with open(path, 'rb') as f:
            params = np.load(io.BytesIO(f.read()), allow_pickle=False)

        return utils.flat_params_to_haiku(params)


    def _load_features(model_featurs: Input[Dataset]):
        features_path = model_features.path
        with open(features_path, 'rb'):
            features = pickle.load(f)
        return features

    
    model_config = config.model_config(model_name)
    # we assume monomer pipeline
    model_config.model.eval.nume_ensemble = num_ensemble
    model_params = _get_model_haiku_params(
        model_name=model_name, data_dir=model_params.path)
    model_runner = model.RunMode(model_config, model_params)
    features = _load_features(model_features)
    logging.info(f'Running prediction using model {model_name}')
    processed_feature_dict = model_runner.process_features(
        feature_dict=features,
        random_seed=random_seed
    )
    prediction_result = model_runner.predict(
        processed_feature_dict,
        random_seed=random_seed
    )
    
    plddt = prediction_result['plddt']
    ranking_confidence = prediction_result['ranking_confidence']
    with open(prediction_result.path, 'wb') as f:
        pickle.dump(prediction_result, f, protocol=4)
    prediction_result.metadata['ranking_confidence']=ranking_confidence
    prediction_result.metadata['data_format']='pkl'

    plddt_b_factors = np.repeat(
        plddt[:, None], residue_constants.atom_type_num, axis=-1)
    unrelaxed_protein = protein.from_prediction(
        features=processed_feature_dict,
        result=prediction_result,
        b_factors=plddt_b_factors,
        remove_leading_feature_dimension=not model_runner.multimer_mode)
    unrelaxed_pdbs = protein.to_pdb(unrelaxed_protein)
    with open(unrelaxed_protein.path, 'w') as f:
        f.write(unrelaxed_pdbs)
    unrelaxed_protein.metadata['data_format']='pdb'






