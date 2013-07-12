#-*- coding=utf-8 -*-

import urllib2
import cookielib
import json
import time
from urllib import urlencode
from irc import *
import last_reply

BASE_URL = "http://avboost.com/"
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
    def __init__(self, url, user, pwd):
        self.URL = url
        self.URL_NEW = url + "new" + DOT_JSON 
        self.URL_T = url  + "t/"
        self.URL_LOGIN = url  + "login"
        self.URL_SESSION = url  + "session"
        self.URL_LATEST = url + "latest" + DOT_JSON

        self.cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self.cookies),
                )
        urllib2.install_opener(self.opener)
        
        data = urlencode({
        "login": user, 
        "password": pwd, 
        })
        self.smoothly_POST(self.URL_SESSION, data)

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

    def get_new(self):
        m = self.smoothly_GET(self.URL_NEW)
        a = json.loads(m)
        ids = []
        for it in a["topic_list"]["topics"]:
            ids.append(it["id"])
        return ids
    
    def smoothly_POST(self, url, data):
        r = urllib2.Request(url, data)
        r.add_header("Referer", self.URL)
        r.add_header("X-Requested-With", "XMLHttpRequest")
        r.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        r.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0")
        return self.opener.open(r).read()
    
    def smoothly_GET(self, url):
        r = urllib2.Request(url)
        r.add_header("Referer", self.URL)
        r.add_header("X-Requested-With", "XMLHttpRequest")
        r.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        r.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0")
        return self.opener.open(r).read()
        
    def url_topic(self, id):
        return self.URL_T + str(id) + DOT_JSON

    def get_topic_author_and_text(self, id):
        a = json.load(urllib2.urlopen(self.url_topic(id)))
        return (a["title"], \
        a["post_stream"]["posts"][0]["username"], \
        strip_text(a["post_stream"]["posts"][0]["cooked"]), id)

    def get_last_reply_author_and_text(self, id):
        a = json.load(urllib2.urlopen(self.url_topic(id)))
        return (a["post_stream"]["posts"][-1]["username"], \
        strip_text(a["post_stream"]["posts"][-1]["cooked"]), id)

    def get_all_new(self):
        a = []
        for it in self.get_new():
            a.append(self.get_topic_author_and_text(it))
        return a
    
    def view_url_topic(self, id, pointed_reply=0):
        if pointed_reply == 0:
            return self.URL_T + "topic/" + str(id)
        else :
            return self.URL_T + "topic/" + str(id) + "/" + str(pointed_reply)
        
if __name__ == "__main__":
    BASE_URL = raw_input("Discourse URL:")
    dmm = DiscourseMilkman(BASE_URL, raw_input("Discourse name:"), raw_input("Discourse password:"))
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
        for it in dmm.get_all_new():
            print it
            send_message(socket_irc, channel, "新主题：" + it[0].encode("utf-8") + "中，" + it[1].encode("utf-8") + "写道：")
            send_message(socket_irc, channel, it[2].encode("utf-8"))
            send_message(socket_irc, channel, dmm.view_url_topic(it[3]))
        new_top = dmm.get_top()
        if new_top != -1:
            if new_top[1] != 1:
                send_message(socket_irc, channel, "主题《" + new_top[0].encode("utf-8") + "》被回复了，目前有" + str(new_top[1]) + "个回复")
                curr_last_reply = dmm.get_last_reply_author_and_text(dmm.top_id)
                send_message(socket_irc, channel, curr_last_reply[0].encode("utf-8") + "写道：" + curr_last_reply[1].encode("utf-8"))
                send_message(socket_irc, channel, dmm.view_url_topic(dmm.top_id, new_top[1]))
        time.sleep(2)
        i += 1
