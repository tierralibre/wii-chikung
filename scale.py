#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time
import select

import subprocess

import numpy
import xwiimote

import util
import asyncoro
import random

#import pysqlite2
#import sqlite3
#import sqlalqchemy 
# global bars
conn = None
_iface = None

class RingBuffer():
    def __init__(self, length):
        self.length = length
        self.reset()
        self.filled = False

    def extend(self, x):
        x_index = (self.index + numpy.arange(x.size)) % self.data.size
        self.data[x_index] = x
        self.index = x_index[-1] + 1

        if self.filled == False and self.index == (self.length-1):
            self.filled = True

    def append(self, x):
        x_index = (self.index + 1) % self.data.size
        self.data[x_index] = x
        self.index = x_index

        if self.filled == False and self.index == (self.length-1):
            self.filled = True


    def get(self):
        idx = (self.index + numpy.arange(self.data.size)) %self.data.size
        return self.data[idx]

    def reset(self):
        self.data = numpy.zeros(self.length, dtype=numpy.int)
        self.index = 0


def dev_is_balanceboard(dev):
    
    time.sleep(2) # if we check the devtype to early it is reported as 'unknown' :(

    iface = xwiimote.iface(dev)
    return iface.get_devtype() == 'balanceboard'

def wait_for_balanceboard():
    print("Waiting for balanceboard to connect..")
    mon = xwiimote.monitor(True, False)
    dev = None

    while True:
        mon.get_fd(True) # blocks
        connected = mon.poll()

        if connected == None:
            continue
        elif dev_is_balanceboard(connected):
            print("Found balanceboard:", connected)
            dev = connected
            break
        else:
            print("Found non-balanceboard device:", connected)
            print("Waiting..")

    return dev

def format_measurement(x):
    return "{0:.2f}".format(x / 100.0)

def print_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    tl, tr, bl, br = map(format_measurement, args)

    print("┌","─" * 21, "┐", sep="")
    print("│"," " * 8, "{:>5}".format(sm)," " * 8, "│", sep="")
    print("├","─" * 10, "┬", "─" * 10, "┤", sep="")
    print("│{:^10}│{:^10}│".format(tl, tr))
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│{:^10}│{:^10}│".format(bl, br))
    print("└","─" * 10, "┴", "─" * 10, "┘", sep="")

    print()
    print()

def store_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    tl, tr, bl, br = map(format_measurement, args)

    # 

    print("┌","─" * 21, "┐", sep="")
    print("│"," " * 8, "{:>5}".format(sm)," " * 8, "│", sep="")
    print("├","─" * 10, "┬", "─" * 10, "┤", sep="")
    print("│tl {:^10}│tr {:^10}│".format(tl, tr))
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│bl {:^10}│ br {:^10}│".format(bl, br))
    print("└","─" * 10, "┴", "─" * 10, "┘", sep="")

    print()
    print()



def measurements(iface):
    p = select.epoll.fromfd(iface.get_fd())
    print("measurements def iface")
    while True:
        p.poll() # blocks

        event = xwiimote.event()
        iface.dispatch(event)

        tl = event.get_abs(2)[0]
	#print("tl")
	#print(tl)
        tr = event.get_abs(0)[0]
        br = event.get_abs(3)[0]
        bl = event.get_abs(1)[0]

        yield (tl,tr,br,bl)

def average_mesurements(ms, max_stddev=55):
    last_measurements = RingBuffer(800)
    #print("average_meaurements called")

    while True:
        weight = sum(ms.next())
        #print("weight {}".format(weight))

        last_measurements.append(weight)

        mean = numpy.mean(last_measurements.data)
        stddev = numpy.std(last_measurements.data)

        if stddev < max_stddev and last_measurements.filled:
            print("yield of average_measurements called")
            yield numpy.array((mean, stddev))


##
def server_proc(coro=None):
    coro.set_daemon()
    while True:
        msg = yield coro.receive()
        print("Message received: {}"),format(msg)



def client_proc(server, n, coro=None):
    #global msg_id
    ready = True
    global _iface
    p = select.epoll.fromfd(_iface.get_fd())
    while ready:
        p.poll() # blocks
        event = xwiimote.event()
        _iface.dispatch(event)

        tl = event.get_abs(2)[0]
    #print("tl")
    #print(tl)
        tr = event.get_abs(0)[0]
        br = event.get_abs(3)[0]
        bl = event.get_abs(1)[0]
        yield (tl,tr,br,bl)
        server.send('tl: {} tr: {} br: {} bl: {}'.format(tl, tr, br, bl))




    # for x in range(3):
    #     yield coro.suspend(random.uniform(0.5,3))
    #     msg_id += 1
    #     print("client_proc send: {}"),format(msg_id)
    #     server.send('%d: %d / %d' % (msg_id, n, x))
    #     server.send('{} {}'.format(msg_id, 'two'))


##
def main():

    if len(sys.argv) == 2:
        device = sys.argv[1]
    else:
        device = wait_for_balanceboard()

    iface = xwiimote.iface(device)
    _iface = iface

    iface.open(xwiimote.IFACE_BALANCE_BOARD)
    print("iface.open balanceboard")

       # test asyncoro
    server = asyncoro.Coro(server_proc)
    #for i in range(10):
    asyncoro.Coro(client_proc, server, 1)
    # end asyncoro
 
    
    exit = False

    while not exit:
        print("exit: {}", exit)
        try:
            for m in measurements(iface):
                print_bboard_measurements(*m)
                print("q to exit else to continue")
                c = sys.stdin.read(1)
                if c == 'q':
                    exit = True
                    break



        except KeyboardInterrupt:
            print("Bye!")

    print("closing device iface")
    _iface.close(xwiimote.IFACE_BALANCE_BOARD)
    print("bt disconnect device")
    subprocess.call(["bt-device", "-d", "Nintendo RVL-WBC-01"])
    #subprocess.call(arg1)
    # poll unregisterp.unregister(mon_fd)
    # device


if __name__ == '__main__':
    main()
