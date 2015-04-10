# Scrape developer.mbed.org for library manifest data

`scrapy crawl mbedlib`

downloads a few project pages and tries to produce manifest files

To create and review data, use the following bash commands:
```
scrapy crawl mbedlib -o libs.jsonlines
cat libs.jsonlines | while read line; do echo "$line"|json_pp -f json -t json -json_opt pretty,utf8; done
```
