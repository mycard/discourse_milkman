#!/usr/bin/python
# -*- coding: utf-8 -*-
 
from pyxmpp.jid import JID
from pyxmpp.message import Message
from pyxmpp.jabber.client import JabberClient
from pyxmpp.jabber.simple import send_message
from pyxmpp.streamtls import TLSSettings
from pyxmpp.jabber.muc import MucRoomState, MucRoomManager, MucRoomHandler
import sys
import locale
import codecs


class Client(JabberClient):
    def __init__(self, jid, password, tls_cacerts = None):
        if tls_cacerts is None:
            tls_cacerts = 'tls_noverify'
        # if bare JID is provided add a resource -- it is required
        if not jid.resource:
            jid=JID(jid.node, jid.domain, "Echobot")

        if tls_cacerts:
            if tls_cacerts == 'tls_noverify':
                tls_settings = TLSSettings(require = True, verify_peer = False)
            else:
                tls_settings = TLSSettings(require = True, cacert_file = tls_cacerts)
        else:
            tls_settings = None

        # setup client with provided connection information
        # and identity data
        JabberClient.__init__(self, jid, password,
                disco_name="PyXMPP example: echo bot", disco_type="bot",
                tls_settings = tls_settings)

        # add the separate components
        # self.interface_providers = [
        #     VersionHandler(self),
        #     EchoHandler(self),
        #     ]

    def session_started(self): 
        """Handle session started event. May be overriden in derived classes. 
        This one requests the user's roster and sends the initial presence.""" 
        print u'SESSION STARTED'
        self.request_roster()
        print u'ConnectToParty'
        self.connectToMUC()


    def stream_state_changed(self,state,arg):
        """This one is called when the state of stream connecting the component
        to a server changes. This will usually be used to let the user
        know what is going on."""
        print "*** State changed: %s %r ***" % (state,arg)

    def print_roster_item(self,item):
        if item.name:
            name=item.name
        else:
            name=u""
        print (u'%s "%s" subscription=%s groups=%s'
                % (unicode(item.jid), name, item.subscription,
                    u",".join(item.groups)) )

    def roster_updated(self,item=None):
        if not item:
            print u"My roster:"
            for item in self.roster.get_items():
                self.print_roster_item(item)
            return
        print u"Roster item updated:"
        self.print_roster_item(item)

    def connectToMUC(self):
        self.roomManager = MucRoomManager(self.stream);
        self.roomHandler = MucRoomHandler()
        self.roomState = self.roomManager.join(
            room=JID('mycard@conference.my-card.in'),
            nick='mindcat',
            handler=self.roomHandler, 
            history_maxchars=0,
            password = None)
        self.roomManager.set_handlers()
        self.roomState.send_message("喵喵喵喵!")

 
if __name__ == '__main__':
    locale.setlocale(locale.LC_CTYPE, "")
    encoding = locale.getlocale()[1]
    if not encoding:
        encoding = "us-ascii"
    sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
    sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")

    ID = ('mindcat@my-card.in', u'foreveralone')
    c = Client(JID(ID[0]),ID[1])
    c.connect()
    try:
    # Component class provides basic "main loop" for the applitation
    # Though, most applications would need to have their own loop and call
    # component.stream.loop_iter() from it whenever an event on
    # component.stream.fileno() occurs.
        c.loop(1)
    except KeyboardInterrupt:
        print u"disconnecting..."
        c.disconnect()