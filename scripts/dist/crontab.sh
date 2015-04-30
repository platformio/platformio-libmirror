#!/bin/bash
#
# add the following line to crontab using `crontab -e` to execute
# every day at 5 am:
#
# 0 5 * * * $HOME/prg/platformio-libmirror/scripts/github-top/crontab.sh
#
# Note that it is not advisable to have two instances running
# at overlapping times.
#
# Also note that add but uncommited files withh be committed and pushed
# when the script ./mk-summary.sh is executed

cd $(dirname $0)/../github-top
git pull >/dev/null 2>/dev/null
./mk-list-platformio.sh >/dev/null 2>/dev/null
./mk-list-accepted.sh >/dev/null 2>/dev/null
./mk-summary.sh >/dev/null 2>/dev/null

cd $(dirname $0)/../mbed-top
./mk-summary.sh >/dev/null 2>/dev/null

git push
