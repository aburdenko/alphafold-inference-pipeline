#!/bin/bash

set -e

trap 'exit_handler $? $LINENO' 1 2 3 15 ERR 

exit_handler() {
    echo 'In exit handler'
    echo "Error $1 occured in line $2"
    
    # Delete orphaned jobs
    for job_id in "${jobs[@]}"
    do
        echo "Deleting job $job_id" 
        ddel --provider local --job "$job_id"
    done
}


echo 'Dsub 1'

jobs=()

job1=$(dsub --provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo 1; sleep 30; exit 1')

jobs+=( "$job1" )

echo 'Dsub 2'

job2=$(dsub --provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo 2; exit 0' \
)

jobs+=( "$job2" )


job3=$(dsub --provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo 3; sleep 600; exit 0')

jobs+=( "$job3" )

job4=$(dsub --provider local \
--logging gs://jk-dsub-staging/sandbox/logging \
--command 'echo 3; sleep 600; exit 0' \
--after "$job1" )

jobs+=( "$job4" )



