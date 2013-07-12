#-*- coding:utf-8 -*-

import urllib2
import json

top_id = 0
top_reply_nr = 0

def get_top(url):
    global top_id
    global top_reply_nr
    URL_LATEST = url + "latest.json"
    top = json.load(urllib2.urlopen(URL_LATEST))["topic_list"]["topics"][0]
    if top_id != top["id"]:
        top_id = top["id"]
        top_reply_nr = top["highest_post_number"]
        return (top["title"], top["highest_post_number"])
    else:
        if top_reply_nr != top["highest_post_number"]:
            top_id = top["id"]
            top_reply_nr = top["highest_post_number"]
            return (top["title"], top["highest_post_number"])
        return -1

def init(url):
    get_top(url)

