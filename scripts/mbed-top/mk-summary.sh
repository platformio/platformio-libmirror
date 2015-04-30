#!/bin/bash

(echo "# TOP libraries overall status"
echo
echo "Repository | Manifest | PIO-Library"
echo "-----------|----------|------------") > TOP-libs-status.md
(echo "# TOP libraries TODO"
echo
echo "Repository | Manifest | PIO-Library"
echo "-----------|----------|------------") > TOP-libs-TODO.md

myrepo="https://raw.githubusercontent.com/platformio/platformio-libmirror/master/"
piourl="http://platformio.org/#!/lib/show/"
(cd ../../; find configs/mbed -type f|sort|grep json$)|while read manifest; do
        no=$(basename $manifest .json|sed -r -e 's/_([^_]+)$/ \1/')
	name=$(echo $no|cut -d\  -f1)
	owner=$(echo $no|cut -d\  -f2)
	manifile=$(basename $manifest)
	repo=$(grep -1 '"hg"' "../../$manifest"|grep '"url"'|cut -d\" -f4)
	pio_lib=$(grep " $repo$" ../github-top/list.platformio.libs|cut -d: -f1|head -1)
	if [ -z "$pio_lib" ] ; then
		echo "[$owner/$name]($repo) | [$manifile]($myrepo$manifest) |" >> TOP-libs-status.md
		echo "[$owner/$name]($repo) | [$manifest]($myrepo$manifest) |" >> TOP-libs-TODO.md
	else
		echo "[$owner/$name]($repo) | [$manifile]($myrepo$manifest) | [$pio_lib]($piourl$pio_lib/$name)" >> TOP-libs-status.md
	fi
done

git add *.md; git commit -m 'automated update using mk-summary.sh'
