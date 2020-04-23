#!/bin/bash

BASE_DIR=$(dirname $0)
PYTHON_PROC_NAME='run_bot.py'

exit_code=1
existing_process=$(ps ax | egrep -v "awk|grep" | grep "$PYTHON_PROC_NAME" | awk '{print $1}')

if [[ $existing_process == "" ]]; then
    printf "Starting Bot!\n"
    source ${BASE_DIR}/env/bin/activate
    python3 ${BASE_DIR}/${PYTHON_PROC_NAME} &
    exit_code=$?
else
    printf "Bot already running with Proc ID ${existing_process}!\n"
    exit_code=11
fi

exit $exit_code

# deactivate
