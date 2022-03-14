#! /bin/bash

# Copyright 2022 Google LLC
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

if [[ -n $1 ]]; then
	git clone https://github.com/deepmind/alphafold.git
	pushd alphafold
	docker build -f docker/Dockerfile -t alphafold .
	docker tag alphafold gcr.io/$1/alphafold
	docker push gcr.io/$1/alphafold
	pip install -r ./pipeline/requirements.txt
        sudo chmod -R 755 ./pipeline	
	export set GOOGLE_APPLICATION_CREDENTIALS=/content/aburdenko-project-d93f3d235d90.json
	sudo ./pipelne/run.py
	popd
fi
