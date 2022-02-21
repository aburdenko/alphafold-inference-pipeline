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

import json 
import logging
import os
import numpy as np
import sys
import pickle


from typing import Any, List, Tuple


def rank(
    prediction_result_paths: List[str], 
) -> Tuple[dict]:
    ranking_confidences = {} 
    for prediction_path in prediction_result_paths:
        file_name = os.path.split(prediction_path)[-1] 
        with open(prediction_path, 'rb') as f:
            prediction = pickle.load(f)
        ranking_confidences[file_name] = prediction['ranking_confidence']
 
    ranked_order = []
    for idx, (model_name, _) in enumerate(
        sorted(ranking_confidences.items(), key=lambda x: x[1], reverse=True)):
        ranked_order.append(model_name)

    rankings ={
        'confidences': ranking_confidences,
        'order': ranked_order,
    } 
    return ranking_confidences, ranked_order 


def _main(
    prediction_result_paths: List[str],
    ranking_output_path: str,
):
    logging.info(f'Ranking predictions')

    ranking_confidences, ranked_order = rank(prediction_result_paths)
    logging.info(f'Writing ranking to {ranking_output_path}')

    with open(ranking_output_path, 'w') as f:
        label = 'plddts'
        f.write(json.dumps(
            {label: ranking_confidences, 'order': ranked_order}, indent=4))
    

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO, 
                        datefmt='%d-%m-%y %H:%M:%S',
                        stream=sys.stdout)

    prediction_results_path = os.environ['PREDICTION_RESULTS_PATH']
    prediction_result_paths = [os.path.join(prediction_results_path, filename) for
                               filename in os.listdir(prediction_results_path)]

    if not prediction_result_paths:
        raise RuntimeError(f'No predictions to rank in {prediction_results_path}')
     
    _main(
        prediction_result_paths=prediction_result_paths,
        ranking_output_path=os.environ['RANKING_RESULTS_PATH']
    )