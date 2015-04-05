# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class RepoPostProc(object):
    def process_item(self, item, spider):
        #
        # transfer deplist1 and deplist2 to appropriate fields:
        #
	self.transfer_if(item,'deplist1','Dependencies:','dependencies')
        self.transfer_if(item,'deplist2','Dependencies:','dependencies')
        self.transfer_if(item,'deplist1','Dependents:','examples')
        self.transfer_if(item,'deplist2','Dependents:','examples')
        # sometimes there is a link to subpage instead:
        if ('repository' in item):
            rep = item['repository']
            if type(rep) is list: rep = rep[0]
            self.transfer_if(item,'deplist2',rep+'dependents','examples')
        # todo: check components if contents need to go to authors or keywords

        return item

    # transfer list in key1 to key2 (except first element) 
    # if first element equals firstval
    def transfer_if(self, item, key1, firstval, key2):
        if key1 in item.keys():
            if item[key1][0] == firstval:
                tmplist = item[key1]
                del tmplist[0]
                newlist = []
                if key2 in item:
                    newlist= item[key2]
                newlist = tmplist
                item[key2] = newlist
                del item[key1]
