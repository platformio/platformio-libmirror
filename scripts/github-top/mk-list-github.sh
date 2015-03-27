#!/bin/bash

rm -f .list.github.top
for ((p=1; $p<=100; p++)); do
	if [ $p -gt 1 ]; then echo "sleeping..."; sleep 12; fi
	echo processing page $p
	curl -s 'https://github.com/search?o=desc&p='$p'&q=arduino+library+&ref=searchresults&s=stars&type=Repositories&utf8=%E2%9C%93' | \
			grep '    <a href="/'|cut -d\" -f2|while read name; do
		echo $name
		echo $name >> .list.github.top
	done
done
mv .list.github.top list.github.top
