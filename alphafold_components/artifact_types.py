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
"""ML Metadata types for inference artifacts."""

from typing import Dict, Optional
from kfp.v2 import dsl
import json

class MSA(dsl.Artifact):
  """An artifact representing an MSA."""
  TYPE_NAME = 'alphafold.MSA'
  VERSION = '0.0.1'

  def __init__(self,
               name: Optional[str] = None,
               uri: Optional[str] = None,
               metadata: Optional[Dict] = None):
    super().__init__(uri=uri, name=name, metadata=metadata)
    
    @property
    def format(self) -> str:
      return self._get_format()

    def _get_format(self) -> str:
      return self.metadata.get('format')

    @format.setter
    def format(self, format:str):
      self._set_format(str)

    def _set_format(self, format:str):
      self.metadata['format'] = format


class Template(dsl.Artifact):
  """An artifact representing a protein template."""
  TYPE_NAME = 'alphafold.Template'

  def __init__(self,
               name: Optional[str] = None,
               uri: Optional[str] = None,
               metadata: Optional[Dict] = None):
    super().__init__(uri=uri, name=name, metadata=metadata)
    
    