job_id=$(dsub \
--provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo test; sleep 60; exit 1')

echo $job_id

dsub \
--provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo next_job' \
--after "$job_id"
