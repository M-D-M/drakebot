#!/bin/bash

BASE_DIR=$(dirname $0)

source ${BASE_DIR}/env/bin/activate

python3 ${BASE_DIR}/run_bot.py &

# deactivate