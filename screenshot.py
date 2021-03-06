#!/usr/bin/env python
# PyMtGoxMon v1.0 - Python-based monitor for MtGox BTC trading!
# Copyright (C) 2013 Albert Huang.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# Screenshot module for PyMtGoxMon. Requires pygtk to run!
# screenshot.py
# 

try:
	import gtk.gdk
	SCREENSHOT_ENABLED = True
except:
	print "WARNING: PyGTK could not be loaded! Screenshots will be disabled."
	#import traceback
	#print traceback.format_exc()
	SCREENSHOT_ENABLED = False

def screenshot(file_name):
	if SCREENSHOT_ENABLED:
		w = gtk.gdk.get_default_root_window()
		sz = w.get_size()
		print "The size of the window is %d x %d" % sz
		pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
		pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
		if (pb != None):
			pb.save(file_name,"png")
			print "Screenshot saved to %s." % file_name
		else:
			print "Unable to get the screenshot."
