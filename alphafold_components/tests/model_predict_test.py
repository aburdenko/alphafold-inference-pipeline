import os

from model_predict import predict


class ArtifactMockup(object):
    def __init__(
        self,
        path: str,
        uri: str,
        metadata: dict):
        self.path = path
        self.uri =uri
        self.metadata=metadata

_model_features = ArtifactMockup(
    path='/artifacts/features.pkl',
    metadata={},
    uri='gs://something'
)   

_model_params = ArtifactMockup(
    path='/data/params',
    metadata={},
    uri='gs://something'
)  

_raw_prediction = ArtifactMockup(
    path='/output/protein/prediction.dat',
    metadata={},
    uri='gs://something'
)   

_unrelaxed_protein = ArtifactMockup(
    path='/output/protein/unrelaxed.pdb',
    metadata={},
    uri='gs://something'
)   


predict(
    model_features=_model_features,
    model_params=_model_params,
    raw_prediction=_raw_prediction,
    unrelaxed_protein=_unrelaxed_protein,
    model_name='model_1',
    num_ensemble=1,
    random_seed=1,
)


