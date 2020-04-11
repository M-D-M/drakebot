#!/bin/bash

LEGEND_TEXT="[ Legend: X (days) - XX (hours) : XX (minutes) : XX (seconds) ]\n"

Servers_Online=$(ps f | egrep ShooterGame | sed -n -e "s/^\([^ ]*\).*SessionName=\([^\?]*\)\?.*/\1=\2/p")
amt_of_servers=$(echo $Servers_Online | tr -cd '=' | wc -c)

if [[ $amt_of_servers -lt 1 ]]; then
    printf "No servers are currently online."
else
    printf "There are $amt_of_servers server(s) currently online.\n\n"
    printf "$LEGEND_TEXT"
    for Server in $Servers_Online
    do
        proc_id=$(printf $Server | cut -d"=" -f1)
        serv_name=$(printf $Server | cut -d"=" -f2)
        proc_lifetime=$(ps -o etime= -p $proc_id | xargs) # xargs trims whitespace

        printf "\nServer Name: $serv_name (Uptime: $proc_lifetime)"
    done
fi
