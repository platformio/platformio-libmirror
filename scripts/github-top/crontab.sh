#!/bin/bash
#
# add the following line to crontab using `crontab -e` to execute
# every day at 5 am:
#
# 0 5 * * * $HOME/prg/platformio-libmirror/scripts/github-top/crontab.sh
#
# Note that it is not advisable to have two instances running
# at overlapping times

cd $(dirname $0)
git pull >/dev/null 2>/dev/null
./mk-list-platformio.sh >/dev/null 2>/dev/null
./mk-list-accepted.sh >/dev/null 2>/dev/null
./mk-summary.sh >/dev/null 2>/dev/null

