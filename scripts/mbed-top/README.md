# Scrape developer.mbed.org for top libraries

`scrapy crawl mbedtop`

will request a list of of libraries (sorted by how many times each library was included
in another mbed hostes library or project) and generate PlatformIO Library Manager 
manifest files. Projects listed as dependents will be interpreted as examples, whereas
libraries listed as dependencies will be included in the list of sources for manifest 
files.

The manifest files are written to the folder ../../configs/mbed/%LIBRARYNAME%_%AUTHOR%.json 
ready to be added to the git repository. After commit and push to github, the files can be 
registered with the platformio library mananger. 

This registration should be handled or at least guided by another automated script to avoid
multiple registrations.


# Scrape developer.mbed.org for library manifest data

`scrapy crawl mbedlib`

downloads a few project pages and tries to produce manifest files

To create and review data, use the following bash commands:
```
scrapy crawl mbedlib -o libs.jsonlines
cat libs.jsonlines | while read line; do echo "$line"|json_pp -f json -t json -json_opt pretty,utf8; done
```
