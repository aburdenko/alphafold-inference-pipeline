#!/bin/bash

set -e

trap 'exit_handler $? $LINENO' 1 2 3 15 ERR 

exit_handler() {
    echo 'In exit handler'
    echo "Error $1 occured in line $2"
    

}


models=( model_1 model_2 model_3 model_4 model_5 )

echo "${models[@]}"

for model in "${models[@]}"
do
    echo "$model"
done





