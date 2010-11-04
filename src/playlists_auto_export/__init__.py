"""
    playlists_auto_export - Rhythmbox plugin

    @author: Jean-Lou Dupont
    
    MESSAGES OUT:
    =============
    - "appname"
    - "devmode"
    - "tick"
    - "load_complete"
    - "playlist"
    - "playlist_created"
    
"""
DEV_MODE=True
PLUGIN_NAME="playlists_auto_export"
TICK_FREQ=4
TIME_BASE=250
MSWITCH_OBSERVE_MODE=True

import os
import sys

curdir=os.path.dirname(__file__)
sys.path.insert(0, curdir)
print curdir

import gobject
import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop

gobject.threads_init()  #@UndefinedVariable
dbus.glib.init_threads()
DBusGMainLoop(set_as_default=True)


import rhythmdb, rb #@UnresolvedImport

from system.base import TickGenerator
from system.mbus import Bus
from helpers.db import EntryHelper

import system.base as base
base.debug=DEV_MODE

import system.mswitch as mswitch
mswitch.observe_mode=MSWITCH_OBSERVE_MODE

#import agents.bridge

#import agents._tester

from helpers.playlists import *


class PlaylistsAutoExportPlugin (rb.Plugin):
    """
    Must derive from rb.Plugin in order
    for RB to use the plugin
    """
    BUSNAME="__pluging__"
    
    def __init__ (self):
        rb.Plugin.__init__ (self)
        self.active=None
        self.current_entry=None
        self.dbcount=0
        self.load_complete=False
        self.done=False
        self.db=None
        self.type_song=None
        self.start_phase=True
        self.current_entries_count=0
        self.previous_entries_count=0
        self.song_entries={}
        self.sourcescb=[]
        
        Bus.subscribe("__pluging__", "devmode?", self.hq_devmode)
        Bus.subscribe("__pluging__", "appname?", self.hq_appname)
        Bus.subscribe("__pluging__", "__tick__", self.h_tick)

    def activate (self, shell):
        """
        Called by Rhythmbox when the plugin is activated
        """
        self.active=True
        self.shell = shell
        self.sp = shell.get_player()
        self.db=self.shell.props.db
        self.sl=shell.props.sourcelist
        self.plm=shell.get_playlist_manager()
        
        ## We might have other signals to connect to in the future
        self.dbcb = (
                     #self.db.connect("entry-added",    self.on_entry_added),
                     #self.db.connect("entry-deleted",  self.on_entry_deleted),
                     #self.db.connect("entry-changed",  self.on_entry_changed),
                     self.db.connect("load-complete",  self.on_load_complete),
                     )
        
        self.slcb = (
                     self.sl.connect("drop-received",  self.on_drop_received),
                     #self.sl.connect("selected",       self.on_selected),
                     )

        self.plcb = (
                     self.plm.connect("playlist-added",   self.on_playlist_added),
                     self.plm.connect("playlist-created", self.on_playlist_created),
                     #self.plm.connect("status-changed",   self.on_status_changed),
                     )
        
        ## Distribute the vital RB objects around
        Bus.publish("__pluging__", "rb_shell", self.shell, self.db, self.sp)
        
        self.type_song=self.db.entry_type_get_by_name("song")
        
    def deactivate (self, shell):
        """
        Called by RB when the plugin is about to get deactivated
        """
        self.active=False
        self.shell = None
        db = shell.props.db
        
        for id in self.dbcb:
            db.disconnect(id)
            
        for id in self.slcb:
            self.sl.disconnect(id)
            
        for id in self.plcb:
            self.plm.disconnect(id)

    ## ================================================  rb signal handlers
    def on_status_changed(self, source):
        if self.active:
            Bus.pub(self.BUSNAME, "playlist_changed", source)
            print "status-changed: %s" % source
    
    def on_playlist_added(self, manager, source):
        Bus.pub(self.BUSNAME, "playlist", source)
        self.sourcescb.append(source.connect("status-changed", self.on_status_changed))
        print "playlist-added: %s" % source
        
    def on_playlist_created(self, manager, source):
        Bus.pub(self.BUSNAME, "playlist_created", source)
        print "playlist-created: %s" % source
    
    def on_selected(self, sourcelist, source):
        """ Testing purposes only
        """
        print "on_selected: %s, %s" % (sourcelist, source)
        ph=PlaylistsHelper(self.shell)
        for l in ph.iter():
            #print "playlist image: %s, name: %s" % (l[1], l[2])
            name, source=ph.itemNameSource(l)
            if name.lower()=="hpc":
                for item in source.props.base_query_model:
                    entry, _path=list(item)
                    print entry
                
    def on_drop_received(self, source, target, data):
        Bus.pub(self.BUSNAME, "playlist_changed", source)
        print "on_drop_received: sl: %s, target: %s, data: %s" % (source, target, data)
    
    
    def on_load_complete(self, *_):
        """
        'load-complete' signal handler
        """
        self.load_complete=True
        Bus.publish("__pluging__", "load_complete")

    ## ================================================ message handlers
    
    def hq_appname(self):
        Bus.publish("__pluging__", "appname", PLUGIN_NAME)
        
    def hq_devmode(self):
        Bus.publish("__pluging__", "devmode", DEV_MODE)

    def h_tick(self, ticks_per_second, 
               second_marker, min_marker, hour_marker, day_marker,
               sec_count, min_count, hour_count, day_count):
        """        
        """
        


def tick_publisher(*p):
    Bus.publish("__main__", "__tick__", *p)

_tg=TickGenerator(1000/TIME_BASE, tick_publisher)
gobject.timeout_add(TIME_BASE, _tg.input)
