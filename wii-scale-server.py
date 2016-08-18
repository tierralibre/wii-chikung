#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Author: Andreas Älveborn
# URL: https://github.com/aelveborn/Wii-Scale
# 
# This file is part of Wii-Scale
# Copyright (C) 2015 Andreas Älveborn
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import wiiboard
import time
import sys
import getopt

from bluetooth import *

# Global
board = None
sleep = True
sensitivity = 30 #kg
calibrate = 0 #kg
config_address = None

def main(argv):
	print "Wii-Scale started"

	global sleep
	global port
	global config_address
	global calibrate
	global board

	ready = False
	sleep = True
	connected = False

	board = wiiboard.Wiiboard()

	# while(true) # loop

	# chek if board is connected
	if not board.isConnected():
		board = wiiboard.Wiiboard()
		# socket sync?

		#if not config_address:
			address = board.discover()
			address = config_address
			board.connect(address)
			print "board connected address: " + address
			total = []
			total.append(board.mass.totalWeight)
			print total


