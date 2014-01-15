#!/usr/bin/env python
# -*- coding: utf8 -*-
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
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# 
import urllib2, json
import datetime
import time

import websocket
import thread

import threading

import re

import ConfigParser

import screenshot
import sound
import color

import os

#######################################################################
# UTF-8 terminal initialization
#######################################################################
import codecs, sys

reload(sys)
sys.setdefaultencoding('utf-8')

#print sys.getdefaultencoding()

if sys.platform == 'win32':
    try:
        import win32console 
    except:
        print "Python Win32 Extensions module is required.\n You can download it from https://sourceforge.net/projects/pywin32/ (x86 and x64 builds are available)\n"
        exit(-1)
    # win32console implementation  of SetConsoleCP does not return a value
    # CP_UTF8 = 65001
    win32console.SetConsoleCP(65001)
    if (win32console.GetConsoleCP() != 65001):
        raise Exception ("Cannot set console codepage to 65001 (UTF-8)")
    win32console.SetConsoleOutputCP(65001)
    if (win32console.GetConsoleOutputCP() != 65001):
        raise Exception ("Cannot set console output codepage to 65001 (UTF-8)")

#import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

#######################################################################
# Variables and Functions
#######################################################################
WEBSOCKET_URL = "wss://websocket.mtgox.com:443/"
global exitNow
exitNow = False

global ENABLE_COLOR, ENABLE_SOUND, ENABLE_SCREENSHOT, screenshot_path
ENABLE_COLOR = True
ENABLE_SOUND = True
ENABLE_SCREENSHOT = True
screenshot_path = "screenshots"

def cprint(str):
	global logfh, ENABLE_COLOR
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
	noColorStr = re.sub("(\033\[)(.+?)(m)", '', str)
	logfh.write("[%s] [PyMtGoxMon] %s\n" % (now, noColorStr))
	logfh.flush()
	if ENABLE_COLOR:
		print "[%s] [PyMtGoxMon] %s" % (now, str)
	else:
		print "[%s] [PyMtGoxMon] %s" % (now, noColorStr)

def celebrate_high_last():
	global ENABLE_SOUND, ENABLE_SCREENSHOT, screenshot_path
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d_%H:%M:%S")
	if ENABLE_SCREENSHOT:
		screenshot.screenshot(os.path.join(screenshot_path, "HIGH_LAST_%s.png") % timeStr)
	if ENABLE_SOUND:
		sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "sharp_echo_AMP.wav"))

def celebrate_high_bid():
	global ENABLE_SOUND, ENABLE_SCREENSHOT, screenshot_path
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d_%H:%M:%S")
	if ENABLE_SCREENSHOT:
		screenshot.screenshot(os.path.join(screenshot_path, "HIGH_BID_%s.png") % timeStr)
	if ENABLE_SOUND:
		sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "sharp_echo_AMP.wav"))

def save_config():
	try:
		fh = open('mtgox_mon_live.cfg', "w")
		config.write(fh)
		fh.close()
	except:
		cprint("[CLIENT] WARNING: Unable to save config! Highest last price is %.2f, and highest bid price is %.2f!", highest_last_price, highest_bid_price)


START_POST	=	[
					{ "channel" : "ticker.BTCUSD", "op" : "mtgox.subscribe" },
					{ "channel" : "trade.lag", "op" : "mtgox.subscribe" },
					{ "channel" : "trade.BTC", "op" : "mtgox.subscribe" },
					#{ "channel" : "depth.BTCUSD", "op" : "mtgox.subscribe" }
				]

def dosend(ws, msg):
	cprint("[  <<  ] %s" % msg)
	ws.send(msg)
	cprint("[  ::  ] [Success]")

global logfh
try:
	logfh = open("mtgox_mon_live.log", "a")
except:
	print "ERROR: Could not open log file for writing!"
	sys.exit(1)

cprint("[CLIENT] Opened log file for writing...")

#######################################################################
# Frozen check
#######################################################################
frozen = getattr(sys, 'frozen', '')

if not frozen:
	# not frozen: in regular python interpreter
	SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
	cprint("[CLIENT] Initializing from script...")
elif frozen in ('dll', 'console_exe', 'windows_exe'):
	# py2exe:
	SCRIPT_DIR = os.path.dirname(sys.executable)
	cprint("[CLIENT] Initializing from compiled Windows executable...")
elif frozen in ('macosx_app',):
	# py2app:
	# Notes on how to find stuff on MAC, by an expert (Bob Ippolito):
	# http://mail.python.org/pipermail/pythonmac-sig/2004-November/012121.html
	SCRIPT_DIR = os.environ['RESOURCEPATH']
	cprint("[CLIENT] Initializing from Mac compiled executable...")
elif frozen:
	SCRIPT_DIR = os.path.dirname(sys.executable)
	cprint("[CLIENT] Initializing from compiled executable...")

#SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

#######################################################################
# Threading Stuff
#######################################################################
class WSThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.websocket = None
		self.doStop = False
	
	def run(self):
		while self.doStop != True:
			try:
				self.websocket = connect_ws()
				self.websocket.run_forever()
				if self.doStop != True:
					cprint("|CLIENT| Detected that the connection closed, trying to restart...")
				else:
					cprint("|CLIENT| Detected program termination, stopping.")
			except:
				pass
		cprint("|CLIENT| Terminating thread...")
	def restart(self):
		self.websocket.close()
	def stop(self):
		self.doStop = True
		self.websocket.close()

#######################################################################
# Websocket Functions
#######################################################################
def on_message(ws, msg):
	global old_lag, old_buy, old_last_buy, diff, lag_time
	global highest_last_price, highest_bid_price
	global lastMsg, cur_lag
	
	lastMsg = time.time()
	
	raw_msg = str(msg)
	jdata = json.loads(raw_msg)
	if 'private' in jdata:
		if jdata['private'] == 'ticker':
			cur_buy = float(jdata['ticker']['buy']['value'])
			last_buy = float(jdata['ticker']['last']['value'])
			if cur_buy != old_buy:
				if old_buy != 0:
					diff = round(cur_buy - old_buy, 2)
					#print "DEBUG: cur_buy is %.2f, old_buy is %.2f, diff is %.2f" % (cur_buy, old_buy, diff)
				else:
					diff = 0
			else:
				diff = 0
			
			cend = "\033[0m"
			if diff < 0:
				sign = "-"
				cstart = "\033[31m"
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "negative_AMP.wav"))
			elif diff > 0:
				sign = "+"
				cstart = "\033[32m"
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "positive_AMP.wav"))
			else:
				sign = "="
				cstart = "\033[33m"
			if (diff != 0) or (old_buy == 0):
				cprint("[BUY$/฿] $%.2f/BTC [Diff: %s%s$%.2f%s] [Highest: $%.2f/BTC]" % (cur_buy, cstart, sign, abs(diff), cend, highest_bid_price))
			old_buy = cur_buy
			
			if cur_buy > highest_bid_price:
				cprint("[BUY$/฿] ALERT: $%.2f/BTC IS THE HIGHEST BID PRICE WE'VE SEEN!" % (cur_buy))
				cprint("[BUY$/฿]        (Previous record: $%.2f/BTC)" % (highest_bid_price))
				highest_bid_price = cur_buy
				config.set("prices", "highest_bid_price", highest_bid_price)
				celebrate_high_bid()
				save_config()
			
			###################################################
			# LAST BUY
			###################################################
			if last_buy != old_last_buy:
				if old_last_buy != 0:
					diff = round(last_buy - old_last_buy, 2)
					#print "DEBUG: cur_buy is %.2f, old_buy is %.2f, diff is %.2f" % (cur_buy, old_buy, diff)
				else:
					diff = 0
			else:
				diff = 0
			
			cend = "\033[0m"
			if diff < 0:
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "negative_AMP.wav"))
				sign = "-"
				cstart = "\033[31m"
			elif diff > 0:
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "positive_AMP.wav"))
				sign = "+"
				cstart = "\033[32m"
			else:
				sign = "="
				cstart = "\033[33m"
			if (diff != 0) or (old_last_buy == 0):
				cprint("[LAST$฿] $%.2f/BTC [Diff: %s%s$%.2f%s] [Highest: $%.2f/BTC]" % (last_buy, cstart, sign, abs(diff), cend, highest_last_price))
			old_last_buy = last_buy
			
			if last_buy > highest_last_price:
				cprint("[BUY$/฿] ALERT: $%.2f/BTC IS THE HIGHEST LAST PRICE WE'VE SEEN!" % (last_buy))
				cprint("[BUY$/฿]        (Previous record: $%.2f/BTC)" % (highest_last_price))
				highest_last_price = last_buy
				config.set("prices", "highest_last_price", highest_last_price)
				celebrate_high_last()
				save_config()
			#cprint("Got ticker: Selling @ $%.2f" % cur_buy)
		elif jdata['private'] == 'lag':
			cur_lag = float(jdata['lag']['age'] / 1000000.0)
			if (cur_lag != old_lag) and (abs(cur_lag - old_lag) > 1):
				# Limit lag posts to every 2 secs
				if time.time() - lag_time > 2:
					cprint("[SERVER] Lag: %.2f seconds" % cur_lag)
					old_lag = cur_lag
				lag_time = time.time()
			else:
				if (time.time() - lag_time > 2) and (cur_lag > 1):
					cprint("[SERVER] Lag: %.2f seconds" % cur_lag)
		
		elif jdata['private'] == 'trade':
			trade_type = jdata['trade']['trade_type']
			amount = float(jdata['trade']['amount'])
			price = float(jdata['trade']['price'])
			
			cend = "\033[0m"
			
			if trade_type == "bid":
				cstart = "\033[32m"
				sym = "^"
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "positiveshort_AMP.wav"))
			elif trade_type == "ask":
				cstart = "\033[31m"
				sym = "v"
				if ENABLE_SOUND:
					sound.play_sound(os.path.join(SCRIPT_DIR, "sounds", "lose_AMP.wav"))
			else:
				cstart = "\033[33m"
				sym = "?"
			
			cprint("[TRADES] %.2f BTC @ $%.2f [%s%s%s]" % (amount, price, cstart, sym, cend))
		else:
			cprint("[  >>  ] %s" % msg)
	else:
		cprint("[  >>  ] %s" % msg)
	if len(msg) == 175:
		ws.close(reason='Bye bye')

def on_error(ws, error):
	print error

def on_close(ws):
	cprint("[ CONN ] Connection closed!")

def on_open(ws):
	def run(*args):
		cprint("[ CONN ] Connected!")
		cprint("[CLIENT] Subscribing to data channels...")
		for POST in START_POST:
			dosend(ws, json.dumps(POST))
		while True:
			time.sleep(1)
		ws.close()
		print "thread terminating..."
	thread.start_new_thread(run, ())

def connect_ws():
	cprint("[ CONN ] Connecting to %s (websocket)..." % WEBSOCKET_URL)
	ws = websocket.WebSocketApp(WEBSOCKET_URL,
								on_message = on_message,
								on_error = on_error,
								on_close = on_close)
	ws.on_open = on_open
	return ws

#######################################################################
# Startup
#######################################################################
config = ConfigParser.ConfigParser()
try:
	cprint("[CLIENT] Looking for configuration file...")
	tfh = open('mtgox_mon_live.cfg', "r")
	config.read('mtgox_mon_live.cfg')
except:
	cprint("[CLIENT] WARNING: Couldn't find or read config file! If this is your")
	cprint("[CLIENT] first time running this, this is normal!")
	cprint("[CLIENT] Creating configuration file...")
	config.add_section("prices")
	config.set("prices", "highest_last_price", 0)
	config.set("prices", "highest_bid_price", 0)
	config.add_section("config")
	config.set("config", "color", 1)
	config.set("config", "sound", 1)
	config.set("config", "screenshot", 1)
	config.set("config", "screenshot_path", "screenshots")
	fh = open('mtgox_mon_live.cfg', "w")
	config.write(fh)
	fh.close()
	config.read('mtgox_mon_live.cfg')

cprint("[CLIENT] Reading configuration file!")

## TODO: replace this mess with an automated config file fixer, using
##       gigantic dict

if not config.has_section("prices"):
	cprint("[CLIENT] WARNING: Configuration file is missing 'prices' section!")
	cprint("[CLIENT]          Will re-add the 'config' section.")
	config.add_section("prices")
	config.set("prices", "highest_last_price", 0)
	config.set("prices", "highest_bid_price", 0)
	fh = open('mtgox_mon_live.cfg', "w")
	config.write(fh)
	fh.close()
	config.read('mtgox_mon_live.cfg')

if not config.has_section("config"):
	cprint("[CLIENT] WARNING: Configuration file is missing 'config' section!")
	cprint("[CLIENT]          Will re-add the 'config' section.")
	config.add_section("config")
	config.set("config", "color", 1)
	config.set("config", "sound", 1)
	config.set("config", "screenshot", 1)
	config.set("config", "screenshot_path", "screenshots")
	fh = open('mtgox_mon_live.cfg', "w")
	config.write(fh)
	fh.close()
	config.read('mtgox_mon_live.cfg')

global highest_last_price, highest_bid_price
highest_last_price = float(config.get("prices", "highest_last_price"))
highest_bid_price = float(config.get("prices", "highest_bid_price"))

ENABLE_COLOR = (int(config.get("config", "color")) == 1)
ENABLE_SOUND = (int(config.get("config", "sound")) == 1)
ENABLE_SCREENSHOT = (int(config.get("config", "screenshot")) == 1)
screenshot_path = config.get("config", "screenshot_path")

cprint("[CLIENT] Loaded configuration file!")
cprint("[CLIENT] Highest last bid price is %.2f, and highest bid price is %.2f!" % (highest_last_price, highest_bid_price))

global old_lag, old_buy, old_last_buy, diff
global lag_time
global lastMsg, cur_lag

lastMsg = time.time()
cur_lag = 0

old_lag = 0
old_buy = 0
old_last_buy = 0
diff = 0
lag_time = 0

#######################################################################
# Main Loop
#######################################################################

if __name__ == "__main__":
	try:
		#websocket.enableTrace(True)
		wsThread = WSThread()
		wsThread.start()
		lastMsg = time.time()
		# Watchdog
		while True:
			if (time.time() - lastMsg) >= ((cur_lag * 5) + 10):
				cprint("[CLIENT] No messages for the past %i seconds, restarting." % (time.time() - lastMsg))
				wsThread.restart()
			#else:
				#pass
				#cprint("[CLIENT] Last message: %i seconds ago (expected delay: %.2f, lag: %.2f)" % ((time.time() - lastMsg), (cur_lag * 5) + 10, cur_lag))
			time.sleep(1)
		#cprint("[CLIENT] Detected that the connection closed, trying to restart...")
	except KeyboardInterrupt:
		cprint("[CLIENT] Detected keyboard interrupt (CTRL-C), exiting.")
		wsThread.stop()
		wsThread.join()
		try:
			fh = open('mtgox_mon_live.cfg', "w")
			config.write(fh)
			fh.close()
		except:
			cprint("[CLIENT] WARNING: Unable to save config! Highest last price is %.2f, and highest bid price is %.2f!", highest_last_price, highest_bid_price)
		try:
			exitNow = True
			cprint("[CLIENT] Closing connection to API server...")
			ws.close()
		except:
			pass
		cprint("[CLIENT] Terminating.")
		try:
			logfh.close()
		except:
			pass
	print "Thanks for using mtgox_mon!"
