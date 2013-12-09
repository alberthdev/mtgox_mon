mtgox_mon - Python MtGox monitor
=================================
Home page: https://github.com/alberthrocks/mtgox_mon

Introduction
-------------
mtgox_mon is a simple yet versatile program to monitor ongoing trade on
the MtGox Bitcoin exchange. It tracks live trades, as well as bid and
last prices as they are changed.

mtgox_mon uses MtGox's websocket API for communicating with the MtGox
API.

Files
------
You can download a binary release of mtgox_mon at:   
https://github.com/alberthrocks/mtgox_mon/releases

Otherwise, you can simply run the Python source directly. You can
download the source code directly from git:

```
git clone https://github.com/alberthrocks/mtgox_mon.git
```

You can also grab a standard source code release archive at:   
https://github.com/alberthrocks/mtgox_mon/releases

**Note that both the source code release and the versioned binary
release are actual versioned releases.** If there are no versions listed
in the link (or the version you were looking for doesn't exist), a
release has not been made yet!

Requirements
-------------
If you are running mtgox_mon directly from Python source, you will need
to install a few modules:

mtgox_mon requires the following modules to be installed:
 * **websocket_client**, found at https://github.com/liris/websocket-client
   You can either download the source and install it directly, or use
   pip to install the module:   
   `pip install websocket-client`   

mtgox_mon can optionally use the following modules, if installed:
 * **PyGTK**, found at http://www.pygtk.org/   
   You can either download the source and install it directly, or use
   pip to install the module:   
   `pip install PyGTK`   
   This module is used to make a screenshot whenever there is a new
   high. Generally used in combination with a browser on
   http://bitcoinity.org/markets...   
 * **PyGame**, found at http://www.pygame.org/
   You can either download the source and install it directly, or use
   pip to install the module:   
   `pip install pygame`   
   This module is used to play sounds on trades, rises/drops in last/bid
   price, and new highs.   
**Included with source**:   
 * **Colorama**, found at https://pypi.python.org/pypi/colorama   
   You can either download the source and install it directly, or use
   pip to install the module:   
   `pip install colorama`   
   This module is used to assist with displaying colorful terminal text
   on Windows. Colorama is already included in the source, so there's no
   need to install it. The only time a system installation of colorama
   may be useful is if the colorama provided in the source is buggy, in
   which a newer system installation can replace the buggy one.   

If you do not have the modules installed, no worries - the functionality
will be disabled, but the program will still run normally.

Setup
------
The first time mtgox_mon starts, it will create a configuration file for
you. The file will look something like this:

```ini
[prices]
highest_last_price = 783.89999
highest_bid_price = 788.005

[config]
color = 1
sound = 1
screenshot = 1
screenshot_path = screenshots
```

If you don't mind the default settings, simply continue. Otherwise,
press CTRL-C to stop mtgox_mon, edit `mtgox_mon_live.cfg`, and restart.

Configuration
--------------
The configuration file is `mtgox_mon_live.cfg` and is an INI formatted
config file. (Python speak: it's a ConfigParser formatted config file.)

The configuration file should only be edited when mtgox_mon is not
running. mtgox_mon makes constant writes to the configuration file based
on its initial read of the configuration and price record changes.
Changes made to the configuration while mtgox_mon is running will almost
always be lost.

**`prices` section:**
 * **`highest_last_price`**: Stores the highest last price. Only change
   if you know the current highest last price.   
   **Values:** valid price     
   **Default value:** 0.00 (inital value)
 * **`highest_bid_price`**: Stores the highest bid price. Only change
   if you know the current highest bid price.   
   **Values:** valid price     
   **Default value:** 0.00 (inital value)

**`config` section:**
 * **`color`**: Enable or disable colorful terminal output. Disable if
   your terminal does not support colors, or if you just hate colorful
   text.   
   **Values:** 1 to enable, 0 to disable   
   **Default value:** 1
 * **`sound`**: Enable or disable sound output on trading events.
   Disable if you do not want to hear sounds when trading events occur.   
   **Values:** 1 to enable, 0 to disable   
   **Default value:** 1
 * **`screenshot`**: Enable or disable screenshot support for records.
   This works best with the bitcoinity.org website showing. Disable if
   you do not wish to take screenshots when a record high occurs.   
   **Values:** 1 to enable, 0 to disable   
   **Default value:** 1
 * **`screenshot_path`**: Path to save screenshots to when a record
   event occurs. Used only if screenshot is set to 1 (enabled).
   **Values:** valid path   
   **Default value:** screenshots

TODO
-----
I'm looking to add GUI support to mtgox_mon in the future. No more
terminals! (Or ugly ones, in the case of Windows' default command
prompt!)

No worries - terminal support will still exist and live forever!

I may also add (armchair) trading support as well. If/when this feature
is implemented, you will need to request a MtGox API key for mtgox_mon
to use.

License
--------
mtgox_mon is licensed under the GPL, v3. The usual notice header:
```
PyMtGoxMon v1.0 - Python-based monitor for MtGox BTC trading!
Copyright (C) 2013 Albert Huang.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

You can find the full license in LICENSE.

A non-legalese version can be found here:
http://www.tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)

mtgox_mon comes bundled with the following sounds:
 * **GUI Sound Effects** by Lokif   
   Found at: http://opengameart.org/content/gui-sound-effects   
   License: Public domain   
   Any modification(s): Amplified in Audacity, extended positive.wav
                        in Audacity
 * **Positive Sounds** by remaxim   
   Found at: http://opengameart.org/content/postive-sounds   
   License: CC-BY-SA 3.0, GPL v2.0, or GPL v3.0   
   Modification(s): Amplified in Audacity
 * **Bad Sound #2** by remaxim   
   Found at: http://opengameart.org/content/bad-sound-2   
   License: CC-BY-SA 3.0, GPL v2.0, or GPL v3.0   
   Modification(s): Amplified in Audacity
