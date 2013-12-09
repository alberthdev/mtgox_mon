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
# Color module for PyMtGoxMon. Requires colorama to run!
# color.py
# 

try:
	import colorama
	print "Using system colorama."
except:
	import colorama_local as colorama
	print "Using script included colorama."

colorama.init()


