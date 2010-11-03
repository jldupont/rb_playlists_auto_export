"""
    Helpers related to RB playlists
        
    Created on 2010-11-02
    @author: jldupont
"""

__all__=["PlaylistsHelper",
         ]

class PlaylistsHelper(object):
    
    def __init__(self, shell):
        self.entries = [x for x in list(shell.props.sourcelist.props.model) 
                        if list(x)[2].lower()=="playlists"]
        
    def iter(self):
        try: 
            iter=self.entries[0].iterchildren()
        except:
            iter=[]
        return iter

    def itemNameSource(self, item):
        try:
            return (item[2], item[3])
        except:
            return (None, None)

        