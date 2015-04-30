#!/bin/bash

(echo "# TOP libraries overall status"
echo
echo "Repository | Manifest | PIO-Library"
echo "-----------|----------|------------") > TOP-libs-status.md
(echo "# TOP libraries TODO"
echo
echo "Repository | Manifest | PIO-Library"
echo "-----------|----------|------------") > TOP-libs-TODO.md

(cd ../../; find configs/mbed -type f|sort|grep json$)|while read manifest; do
	repo=$(grep -1 '"hg"' "../../$manifest"|grep '"url"'|cut -d\" -f4)
	pio_lib=$(grep " $repo$" ../github-top/list.platformio.libs|cut -d: -f1)
	echo "$repo | $manifest | $pio_lib" >> TOP-libs-status.md
	if [ -z "$pio_lib" ] ; then
		echo "$repo | $manifest | $pio_lib" >> TOP-libs-TODO.md
	fi
done

git add *.md; git commit -m 'automated update using mk-summary.sh'
