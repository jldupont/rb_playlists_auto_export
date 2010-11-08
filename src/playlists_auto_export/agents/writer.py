"""
    Writer Agent - writes the playlists on disk at most every 1 minute
        
    Messages Processed:
    -------------------
    - "playlist_changed"
    
        
    Created on 2010-11-07
    @author: jldupont
"""
from playlists_auto_export.system.base import AgentThreadedBase

class WriterAgent(AgentThreadedBase):

    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.changed={}
        
    def h_tick(self, ticks_second, 
               tick_second, tick_min, tick_hour, tick_day, 
                sec_count, min_count, hour_count, day_count):
        """
        Time base - used to rate limit updates to the playlists files on disk
        """
        if tick_min:
            pass
            
    
    def h_playlist_changed(self, source):
        """ Received when a playlist source changes
        """
        try: 
            self.changed[source.props.name]=source
        except:
            pass
        
        
_=WriterAgent()
_.start()
