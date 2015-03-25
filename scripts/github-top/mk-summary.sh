#!/bin/bash
git pull
(cat list.github.top |tr / " " |while read name rep; do
	remark=""
	if grep -q /$name/$rep$ list.platformio.libs; then
		echo -n O
		remark=$(grep /$name/$rep$ list.platformio.libs|cut -d: -f1|while read l; do echo -n "$l "; done)
	else
		if grep -q /$rep$ list.platformio.libs; then
			echo -n "-"
			remark="possible duplicate of "$(grep /$rep$ list.platformio.libs|head -1)
		else
			if grep -q ^/$name/$rep$ list.github.ignore || grep -q ^/$name/$rep: list.github.ignore; then
				echo -n "I"
				remark=$(grep ^/$name/$rep: list.github.ignore|cut -d: -f2|head -1)
			else
				echo -n -
				remark=$(find $HOME/prg/libs.* -maxdepth 1 -type d -name $rep|sed -e "s!^$HOME/prg!!"|cut -d/ -f2|cut -d. -f2)
			fi
		fi
	fi
	echo " /$name/$rep $remark"
done) > summary

(echo "# TOP libraries overall status"
echo
echo "Status | Repository | Comment"
echo "-------|------------|--------"
cat summary| while read s r c; do 
  echo $(echo $s|sed -e s/O/active/ -e s/#/unclear/ -e s/I/ignored/) "| [$r](http://github.com$r) | $c"
done) > TOP-libs-status.md
(echo "# TOP libraries TODO"
echo
echo "Status | Repository | Comment"
echo "-------|------------|--------"
grep "^- " TOP-libs-status.md
) > TOP-libs-TODO.md

git add list* *.md; git commit -m 'automated update using mk-summary.sh'; git push
