"""
    Various OS functions

    @author: jldupont
    @created on 2011-03-01
        
"""

__all__=[]

def mounts():
    """
    Retrieves the mount points
    
    @return: list of [src_path, mount_point, filesystem_type, options, p1, p2]
    """
    file=open("/proc/mounts", "r")
    _mounts=file.read().split("\n")
    file.close()
    
    result=[]
    for mount in _mounts:
        bits=mount.split(' ')
        result.append(bits)
    return result

def lookup_mount(path, trylowercase=False):
    """
    Lookup a mount record for the specified path
    @returns: None or [mount ...] 
    """
    _mounts=mounts()
    for mount in _mounts:
        if mount[0]==path:
            return mount
        if trylowercase:
            if mount[0].lower()==path.lower():
                return mount
    return None

if __name__=="__main__":
    print mounts()
    
    print lookup_mount("//NAS/Music/", trylowercase=True)==lookup_mount("//nas/music/", trylowercase=True)
            