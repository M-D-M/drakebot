#!/bin/bash

. /home/webuser/bin/drakebot3/bin/activate
. /var/tmp/share/src/ENV.bash
drake_output=/tmp/drakebot.out

/home/webuser/bin/drakebot3/drakebot.py > $drake_output &
