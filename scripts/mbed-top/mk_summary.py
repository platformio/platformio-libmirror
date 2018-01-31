import os
import json
from prettytable import PrettyTable
from subprocess import call,run
head_file = "# Mbed Libs\n"
top_libs_string = "Repository | Manifest | PIO-Library\n"
top_libs_string_1 = "-----------|----------|------------\n"
# print(top_libs_string)
json_dir = "../../configs/mbed/"
json_list = os.listdir(json_dir)
# t = PrettyTable(["Owner","Library"])
f = open('Lib_status.md','w')
f.write(head_file)
f.write(top_libs_string)
f.write(top_libs_string_1)
for i in json_list:
	if(i !="moderation"):
		print(i)
		data = json.load(open(json_dir+i))
		url =data['repository']['url']
		print(len(url))
		author = data['authors']['name']
		repo_name = data['name']
		print(repo_name)
		if isinstance(url, str):
			f.write(('['+author+'/'+ repo_name+']'+"("+url+")" + " | "+ i +' |  \n'))
		else:
			f.write(('['+author+'/'+ repo_name+']'+"("+url['url']+")" + " | "+ i +' |  \n'))
f.write("\n\rTotal libs : "+str(len(json_list)-1)+"\n\r")
f.close()
run(['git','add','Lib_status.md'])
run(['git','commit','-m',"'automated update Lib_status.md'"])
