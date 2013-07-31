#-*- coding=utf-8 -*-

import urllib2
import cookielib
import json
import time
from urllib import urlencode
from irc import *

DOT_JSON = ".json"

def strip_text(text):
    a = text.split("<")
    s = a[0]
    for it in a[1:]:
        aa = it.split(">")
        s += aa[1]
    s = "".join(s.split("\n"))
    if len(s) > 100:
        s = s[:100]
    return s + u"……"

class DiscourseMilkman:
    def __init__(self, url):
        self.URL = url
        self.URL_NEW = url + "new" + DOT_JSON 
        self.URL_T = url  + "t/"
        self.URL_LOGIN = url  + "login"
        self.URL_SESSION = url  + "session"
        self.URL_LATEST = url + "latest" + DOT_JSON

        self.top_id = 0
        self.top_reply_nr = 0
        self.get_top()

    def get_top(self):
        top = json.load(urllib2.urlopen(self.URL_LATEST))["topic_list"]["topics"][0]
        if self.top_id != top["id"]:
            self.top_id = top["id"]
            self.top_reply_nr = top["highest_post_number"]
            return (top["title"], top["highest_post_number"])
        else:
            if self.top_reply_nr != top["highest_post_number"]:
                self.top_id = top["id"]
                self.top_reply_nr = top["highest_post_number"]
                return (top["title"], top["highest_post_number"])
            else:
                return -1

    def url_topic(self, id, pointed_reply=0):
        if pointed_reply == 0:
            return self.URL_T + str(id) + DOT_JSON
        else :
            return self.URL_T + str(id) + "/" + str(pointed_reply) + DOT_JSON

    def get_topic_author_and_text(self, id):
        a = json.load(urllib2.urlopen(self.url_topic(id)))
        return (a["title"], \
        a["post_stream"]["posts"][0]["username"], \
        strip_text(a["post_stream"]["posts"][0]["cooked"]), id)

    def get_last_reply_author_and_text(self, id):
        a = json.load(urllib2.urlopen(self.url_topic(id)))
        hpn = a["highest_post_number"]
        if hpn >= len(a["post_stream"]["posts"]):
            a = json.load(urllib2.urlopen(self.url_topic(id, hpn)))
        return (a["post_stream"]["posts"][-1]["username"], strip_text(a["post_stream"]["posts"][-1]["cooked"]), id)
    
    def view_url_topic(self, id, pointed_reply=0):
        if pointed_reply == 0:
            return self.URL_T + "topic/" + str(id)
        else :
            return self.URL_T + "topic/" + str(id) + "/" + str(pointed_reply)

if __name__ == "__main__":
    BASE_URL = raw_input("Discourse URL:")
    dmm = DiscourseMilkman(BASE_URL)
    channel = raw_input("IRC Channel:#")
    socket_irc = login_irc_freenode(raw_input("IRC nick:"))
    join_chatroom(socket_irc, channel)
    i = 0
    while 1:
        try:
            s = socket_irc.recv(0xffff)
        except:
            pass
        if (i % 10) == 0:
            ping(socket_irc)
        new_top = dmm.get_top()
        if new_top != -1:
            if new_top[1] == 1:
                it = dmm.get_topic_author_and_text(dmm.top_id)
                print "N TOPIC ID %d" % dmm.top_id
                send_message(socket_irc, channel, "新主题：" + it[0].encode("utf-8") + "中，" + it[1].encode("utf-8") + "写道：")
                send_message(socket_irc, channel, it[2].encode("utf-8"))
                send_message(socket_irc, channel, dmm.view_url_topic(dmm.top_id))
            else:
                print "N REPLY UNDER %d NR %d" % (dmm.top_id, new_top[1])
                send_message(socket_irc, channel, "主题《" + new_top[0].encode("utf-8") + "》被回复了，目前有" + str(new_top[1]) + "个回复")
                curr_last_reply = dmm.get_last_reply_author_and_text(dmm.top_id)
                send_message(socket_irc, channel, curr_last_reply[0].encode("utf-8") + "写道：" + curr_last_reply[1].encode("utf-8"))
                send_message(socket_irc, channel, dmm.view_url_topic(dmm.top_id, new_top[1]))
        time.sleep(1)
        i += 1
