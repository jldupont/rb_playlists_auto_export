"""
    M3U utils
        
    Created on 2010-11-08
    @author: jldupont
"""
import os

class M3Uwriter(object):
    
    def __init__(self, path):
        self.path=os.path.expanduser(path)
    
    def write(self, liste):
        try:
            file=open(self.path, "w")
            file.write("#EXTM3U\n\n")
            for item in liste:
                file.write("%s\n" % item)
        finally:
            try:    file.close()
            except: pass