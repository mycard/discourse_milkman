#-*- coding:utf-8 -*-

import socket

def login_irc_freenode(nick):
    s = socket.create_connection(("irc.freenode.net", 6666))
    s.settimeout(0)
    s.send("NICK " + nick + "\r\n")
    s.send("USER " + nick + " 0 * : " + nick + "\r\n")
    return s

def join_chatroom(s, chatroom):
    s.send("JOIN #" + chatroom + "\r\n")

def send_message(s, chatroom, msg):
    s.send("PRIVMSG #" + chatroom + " :" + msg + "\r\n")

def ping(s):
    s.send("PING irc.freenode.net\r\n")

def quit_irc(s):
    s.send("QUIT\r\n")


