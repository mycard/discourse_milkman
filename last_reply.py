#-*- coding:utf-8 -*-

import urllib2
import json

top_id = 0

def get_top(url):
    global top_id
    URL_LATEST = url + "latest.json"
    top = json.load(urllib2.urlopen(URL_LATEST))["topic_list"]["topics"][0]
    if top_id != top["id"]:
        top_id = top["id"]
        return (top["title"], top["highest_post_number"])
    else:
        return -1

def init(url):
    get_top(url)

