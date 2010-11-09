"""
    Writer Agent - writes the playlists on disk at most every 1 minute
        
    Messages Processed:
    -------------------
    - "playlist_changed"
    
        
    Created on 2010-11-07
    @author: jldupont
"""
import os
import urllib

from playlists_auto_export.system.base import AgentThreadedWithEvents
from playlists_auto_export.helpers.db import EntryHelper
from playlists_auto_export.helpers.m3u import M3Uwriter

class WriterAgent(AgentThreadedWithEvents):

    BASE_PATH="~/Music"

    TIMERS_SPEC=[    
        ("min", 1, "t_min")
    ]
    
    def __init__(self):
        AgentThreadedWithEvents.__init__(self)
        self.changed={}
        self.shell=None
        self.db=None
        
    def t_min(self, *_):
        """
        Time base - used to rate limit updates to playlists files on disk
        """
        for name, source in self.changed.iteritems():
            self._process(name, source)
        self.changed={}
            
    
    def h_playlist_changed(self, shell, db, source):
        """ Received when a playlist source changes
        """
        self.shell=shell
        self.db=db
        try: 
            self.changed[source.props.name]=source
            print "WriterAgent.h_playlist_changed: %s" % source.props.name
        except:
            pass
        
    def _process(self, name, source):
        items=[]
        for item in source.props.base_query_model:
            dbentry, _id=list(item)
            entry=EntryHelper.track_details2(self.db, dbentry)
            
            try:
                p=urllib.unquote(entry["path"]).decode("utf8")
                items.append(p)
            except Exception,e:
                print "! unable to decode 'path' for entry: %s" % entry #entry["path"]
                return
            
            try:
                path=os.path.join(self.BASE_PATH, name)+".m3u"
                w=M3Uwriter(path)
                w.write(items)
            except Exception,e:
                print "! Issue (%s) whilst writing .m3u file to path: %s" % (e, path)
            

        
        
        
_=WriterAgent()
_.start()
