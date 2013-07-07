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
    
    def smoothly_GET(self, url, referer="", add_t=False):
        r = urllib2.Request(url)
        if referer == "":
            referer = self.URL
        r.add_header("Referer", referer)
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

    def get_all_new(self):
        a = []
        for it in self.get_new():
            a.append(self.get_topic_author_and_text(it))
        return a
    
    def view_url_topic(self, id):
        return self.URL_T + "topic/" + str(id)
        
if __name__ == "__main__":
    BASE_URL = raw_input("Discourse URL:")
    last_reply.init(BASE_URL)
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
            time.sleep(1)
        new_top = last_reply.get_top(BASE_URL)
        if new_top != -1:
            if new_top[1] != 1:
                send_message(socket_irc, channel, "主题" + new_top[0].encode("utf-8") + "被顶了上来，目前有" + str(new_top[1]) + "个回复")
                send_message(socket_irc, channel, dmm.view_url_topic(last_reply.top_id))
        time.sleep(2)
        i += 1
