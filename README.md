mtgox_mon - Python MtGox monitor
=================================

Introduction
-------------

Requirements
-------------
mtgox_mon requires the following modules to be installed:
 * websocket_client, found at https://github.com/liris/websocket-client
 * PyGTK, found at http://www.pygtk.org/

The PyGTK dependency can be mitigated by changing the `screenshot.py` file to the following:
```python
#!/usr/bin/env python
# PyMtGoxMon v1.0 - Python-based monitor for MtGox BTC trading!
# Copyright (C) 2013 Albert Huang.
# Under GPL v3.
#
# Screenshot module for PyMtGoxMon. Requires pygtk to run!
# screenshot.py
def screenshot(file_name):
    print "WARNING: No screenshot will be taken for this record."
    pass
```

This will be fixed in the near future.

