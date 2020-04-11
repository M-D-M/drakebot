#!/bin/bash

ARK_LOG_DIR=~/log/ARK.logs/

OLDEST_CURRENT_SERVER_LOG=$(ls -h ${ARK_LOG_DIR}Shooter* | egrep -v backup | head -1)

function getOnlineLogOutput {
    # Pass either a string of "joined this" or "left this"

    find $ARK_LOG_DIR -regextype sed -regex ".*/ServerGame.*.log" -newer $OLDEST_CURRENT_SERVER_LOG -type f -print | xargs awk -F ": " -v ark_regex="$1" '$0~ark_regex{print $2}'
}

amt_joined=$(getOnlineLogOutput "joined this" | wc -l)
amt_left=$(getOnlineLogOutput "left this" | wc -l)
(( amt_online=amt_joined-amt_left ))
echo $amt_joined
echo $amt_left
echo $amt_online
getOnlineLogOutput "joined this" | tail -$amt_online | awk '{print $1}'
