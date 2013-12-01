#!/usr/bin/env python
# PyMtGoxMon v1.0 - Python-based monitor for MtGox BTC trading!
# Copyright (C) 2013 Albert Huang.
# Under GPL v3.
# -*- coding: utf8 -*-
import urllib2, json
import datetime
import time

import websocket
import thread

import re

import ConfigParser

import screenshot

from ws4py.client.threadedclient import WebSocketClient
from bs4 import BeautifulSoup

global exitNow
exitNow = False

def cprint(str):
	global logfh
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
	noColorStr = re.sub("(\033\[)(.+?)(m)", '', str)
	logfh.write("[%s] [PyMtGoxMon] %s\n" % (now, noColorStr))
	logfh.flush()
	print "[%s] [PyMtGoxMon] %s" % (now, str)

def celebrate_high_last():
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d_%H:%M:%S")
	screenshot.screenshot("HIGH_LAST_%s.png" % timeStr)

def celebrate_high_bid():
	now = datetime.datetime.now()
	timeStr = now.strftime("%Y-%m-%d_%H:%M:%S")
	screenshot.screenshot("HIGH_BID_%s.png" % timeStr)

def save_config():
	try:
		fh = open('mtgox_mon_live.cfg', "w")
		config.write(fh)
		fh.close()
	except:
		cprint("[CLIENT] WARNING: Unable to save config! Highest last price is %.2f, and highest bid price is %.2f!", highest_last_price, highest_bid_price)

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
	fh = open('mtgox_mon_live.cfg', "w")
	config.write(fh)
	fh.close()

cprint("[CLIENT] Reading configuration file!")

global highest_last_price, highest_bid_price
highest_last_price = float(config.get("prices", "highest_last_price"))
highest_bid_price = float(config.get("prices", "highest_bid_price"))

cprint("[CLIENT] Loaded configuration file!")
cprint("[CLIENT] Highest last bid price is %.2f, and highest bid price is %.2f!" % (highest_last_price, highest_bid_price))

global old_lag, old_buy, old_last_buy, diff
global lag_time
old_lag = 0
old_buy = 0
old_last_buy = 0
diff = 0
lag_time = 0
def on_message(ws, msg):
	global old_lag, old_buy, old_last_buy, diff, lag_time
	global highest_last_price, highest_bid_price
	
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
			elif diff > 0:
				sign = "+"
				cstart = "\033[32m"
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
				sign = "-"
				cstart = "\033[31m"
			elif diff > 0:
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
			elif trade_type == "ask":
				cstart = "\033[31m"
				sym = "v"
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
	global exitNow
	if exitNow:
		cprint("[ CONN ] Connection closed!")
	else:
		cprint("[ CONN ] Connection closed! Trying to restart...")

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
	ws.run_forever()

WEBSOCKET_URL = "wss://websocket.mtgox.com:443/"

if __name__ == "__main__":
	try:
		#websocket.enableTrace(True)
		connect_ws()
	except KeyboardInterrupt:
		cprint("[CLIENT] Detected keyboard interrupt (CTRL-C), exiting.")
		try:
			fh = open('mtgox_mon_live.cfg', "w")
			config.write(fh)
			fh.close()
		except:
			cprint("[CLIENT] WARNING: Unable to save config! Highest last price is %.2f, and highest bid price is %.2f!", highest_last_price, highest_bid_price)
		try:
			logfh.close()
		except:
			pass
		try:
			exitNow = True
			cprint("[CLIENT] Closing connection to API server...")
			ws.close()
		except:
			pass
