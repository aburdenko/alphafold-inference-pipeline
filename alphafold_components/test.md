docker run -it --rm --entrypoint /bin/bash \
-v /home/jupyter/alphafold-inference-pipeline:/src \
-v /mnt/disks/alphafold-datasets:/data \
gcr.io/jk-mlops-dev/alphafold-components

export PYTHONPATH=/src/alphafold_components

pytest -s dsub_wrapper_test.py::test_jackhmmer_job

pytest -s dsub_wrapper_test.py::test_hhblits_job

pytest -s dsub_wrapper_test.py::test_hhsearch_job 

