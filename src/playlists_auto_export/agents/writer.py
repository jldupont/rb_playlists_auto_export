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
from playlists_auto_export.system.os import filtered_mounts, lookup_mount

class WriterAgent(AgentThreadedWithEvents):

    BASE_PATH="~/Music/rb"

    TIMERS_SPEC=[    
        ("sec", 10, "t_min")
    ]
    
    def __init__(self):
        AgentThreadedWithEvents.__init__(self)
        self.changed={}
        self.shell=None
        self.db=None
        
        try:
            p=os.path.expanduser(self.BASE_PATH)
            os.makedirs(p)
        except:
            pass
        
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
        mounts=filtered_mounts()
        mount_printed=False
        
        items=[]
        for item in source.props.base_query_model:
            dbentry, _id=list(item)
            entry=EntryHelper.track_details2(self.db, dbentry)
            
            try:
                p=urllib.unquote(entry["path"]).decode("utf8")
                
            except Exception,e:
                print "! unable to decode 'file location' for entry: %s" % entry
                continue
        
            ### clean up the "file://" and "smb:" prefixes
            p=p.replace("file://","").replace("smb:", "")
            
            ### replace the unc mounting points with file:// based ones
            mount=lookup_mount(p, allmounts=mounts, matchstart=True, trylowercase=True)
            if mount is not None:

                try:
                    oldprefix=mount[0]
                    newprefix=mount[1]
                except:
                    print "!! issue with mount: ", mount
                
                if (oldprefix.endswith("/") and (not newprefix.endswith("/"))):
                    newprefix += "/"
                    
                if not mount_printed:
                    print "> found mount: %s" % mount
                    print "> oldprefix:   %s" % mount[0]
                    print "> newprefix:   %s" % mount[1]
                    mount_printed=True
                    
                p=p.replace(oldprefix, newprefix)
                
                ## as stupid as it is...
                p=p.replace(oldprefix.lower(), newprefix)
            
            ### Add the item to the list
            items.append(p)
            
        try:
            path=os.path.join(self.BASE_PATH, name)+".m3u"
        except:
            print "! Issue with building filesystem path for playlist name: %s" % name
            return
        
        try:
            w=M3Uwriter(path)
            w.write(items)
        except Exception,e:
            print "! Issue (%s) whilst writing .m3u file to path: %s" % (e, path)
            

        
        
        
_=WriterAgent()
_.start()
