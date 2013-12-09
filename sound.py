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
# Simple sound module for PyMtGoxMon. Requires pygame to run!
# sound.py
# 

try:
	import pygame
	SOUND_ENABLED = True
except:
	print "WARNING: PyGame could not be loaded! Sound playback will be disabled."
	#import traceback
	#print traceback.format_exc()
	SOUND_ENABLED = False

# Do some initializations
if SOUND_ENABLED:
	pygame.mixer.init()

def play_sound(filename):
	if SOUND_ENABLED:
		sound = pygame.mixer.Sound(filename)
		sound.play()
