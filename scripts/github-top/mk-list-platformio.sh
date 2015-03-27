#!/bin/bash

# [ -d .json ] || mkdir .json

total=$(curl -s http://api.platformio.org/lib/search|sed -e s/,/\\n/g|grep total|cut -d: -f2)

for ((i=1; $i <= $total; i++)); do
	echo -en "\r$i/$total: " >&2
	confurl=$(curl -s http://api.platformio.org/lib/info/$i|sed -e s/,/,\\n/g|grep confurl|cut -d\" -f4)
	[ -z "$confurl" ] && total=$(expr $total + 1)
	# curl -s "$confurl" > .json/$i
	repo=$(curl -s "$confurl" |while read line; do echo -n $line|sed -e s/\\n//; done| sed -e s/\}/\\n/g|grep repository|sed -e s/,/\\n/g|grep url|cut -d\" -f4)
	[ -n "$repo" ] && echo $i: $(echo $repo|sed -e s/.git$//)
done > .list.platformio.libs
mv .list.platformio.libs list.platformio.libs
echo >&2
