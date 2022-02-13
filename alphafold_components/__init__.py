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

#import os
#
#try:
#  from kfp.v2.components import load_component_from_file
#except ImportError:
#  from kfp.components import load_component_from_file
#
#DbSearchOp = load_component_from_file(
#    os.path.join(
#        os.path.dirname(__file__),
#        'db_search/component.yaml'))

from alphafold_components.msa_search import msa_search as MSASearchOp
from alphafold_components.template_search import template_search as TemplateSearchOp