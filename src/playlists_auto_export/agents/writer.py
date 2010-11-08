"""
    Writer Agent - writes the playlists on disk at most every 1 minute
        
    Messages Processed:
    -------------------
    - "playlist_changed"
    
        
    Created on 2010-11-07
    @author: jldupont
"""
from playlists_auto_export.system.base import AgentThreadedBase
from playlists_auto_export.helpers.db import EntryHelper

class WriterAgent(AgentThreadedBase):

    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.changed={}
        self.shell=None
        self.db=None
        
    def h_tick(self, ticks_second, 
               tick_second, tick_min, tick_hour, tick_day, 
                sec_count, min_count, hour_count, day_count):
        """
        Time base - used to rate limit updates to the playlists files on disk
        """
        if tick_min:
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
        for item in source.props.base_query_model:
            dbentry, _id=list(item)
            entry=EntryHelper.track_details2(self.db, dbentry)
            print entry.path

        
        
_=WriterAgent()
_.start()
