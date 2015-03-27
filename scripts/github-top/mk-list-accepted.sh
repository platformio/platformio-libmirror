#!/bin/bash

# [ -d .json ] || mkdir .json

total=$(curl -s http://api.platformio.org/lib/search|sed -e s/,/\\n/g|grep total|cut -d: -f2)

(
echo "# Libraries with accepted pull-requests"
echo
echo "ID | Project Repository | Manifest Repository | Project Manifest URL"
echo "---|--------------------|---------------------|---------------------"

for ((i=1; $i <= $total; i++)); do
	echo -en "\r$i/$total: " >&2
	confurl=$(curl -s http://api.platformio.org/lib/info/$i|sed -e s/,/,\\n/g|grep confurl|cut -d\" -f4)
	[ -z "$confurl" ] && total=$(expr $total + 1)
	# curl -s "$confurl" > .json/$i
	repo=$(curl -s "$confurl" |while read line; do echo -n $line|sed -e s/\\n//; done| sed -e s/\}/\\n/g|grep repository|sed -e s/,/\\n/g|grep url|cut -d\" -f4)
	owner=$(echo $repo|cut -d/ -f4,5|sed -e s/.git$//)
	cfreg=$(echo $confurl|cut -d/ -f4,5)
	if [ -n "$repo" -a "$owner" != "$cfreg" ]; then
		ownurl="https://raw.githubusercontent.com/$owner/master/"$(echo $confurl|cut -d/ -f6-)
		curl -sf "$ownurl" > /dev/null || ownurl=""
		#[ -n "$ownurl ] && \
		echo "$i | [$owner]($repo) | [$cfreg]($confurl) | $ownurl"
	fi
done ) > .list.accepted
mv .list.accepted list.accepted.md
echo >&2
