###############################################################################
#
# Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################
from __future__ import print_function
from __future__ import division

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

import xwiimote
import time
import sys
from select import poll, POLLIN
import subprocess
import json

###

# from __future__ import print_function

# import sys
# import time
# import select

# import subprocess

# import numpy


###


class AppSession(ApplicationSession):

    log = Logger()
    dev = None
    mon = None
    _iface = None
    _connected = None
    _sendBalanceData = False
    _disconnect = False

    ###
    ### balance board

    ###

    @inlineCallbacks
    def onJoin(self, details):

        
        #
        #device = wait_for_balanceboard()
       
        ### end balance board

        # SUBSCRIBE to a topic and receive events
        #
        sendHello = False
        def onhello(msg):
            self.log.info("event for 'onhello' received: {msg}", msg=msg)




        yield self.subscribe(onhello, 'com.example.onhello')
        self.log.info("subscribed to topic 'onhello'")

        # REGISTER a procedure for remote calling
        #
        def add2(x, y):
            self.log.info("add2() called with {x} and {y}", x=x, y=y)
            return x + y

        yield self.register(add2, 'com.example.add2')
        self.log.info("procedure add2() registered")

                ###

        def dev_is_balanceboard(dev):
            self.log.info("dev is balance board?" )
            time.sleep(2) # if we check the devtype to early it is reported as 'unknown' :(

            iface = xwiimote.iface(dev)
            return iface.get_devtype() == 'balanceboard'

        def wait_for_balanceboard(x, y):
            #print("Waiting for balanceboard to connect..")
            self.log.info("wait for balance board received: {x} and {y}", x=x, y=y)
            mon = xwiimote.monitor(True, False)

            while True:
                mon.get_fd(True) # blocks
                connected = mon.poll()

                if connected == None:
                    self.log.info("wating for connection" )
                    continue
                else:
                    # so wea are connected
                    time.sleep(2) # if we check the devtype to early it is reported as 'unknown' :(
                    iface = xwiimote.iface(connected)
                    #_connected = connected
                    if iface.get_devtype() == 'balanceboard':
                        #yield self.publish('com.example.oncounter', "balanceBoard connected")
                        self.log.info("found balance board, you can step on it to send data" )
                        self._iface = iface
                        self._sendBalanceData = True
                        break
                    
            #return true
            return "Board Found"
        ###
        yield self.register(wait_for_balanceboard, 'com.example.balance')
        self.log.info("procedure wait_for_balanceboard() registered")
        ###

        @inlineCallbacks
        def disconnect_balanceboard():
            self._sendBalanceData
            self.log.info("closing device iface")
            #check if iface is opened?
            self._iface.close(xwiimote.IFACE_BALANCE_BOARD)
            self.log.info("bt disconnect device")
            subprocess.call(["bt-device", "-d", "Nintendo RVL-WBC-01"])
            self._disconnect = True
            self._sendBalanceData = False
            yield "Done"

        yield self.register(disconnect_balanceboard, 'com.example.balance.disconnect')
        self.log.info("procedure disconnect_balanceboard() registered")
        ####

        ###
        def starMonitoringBoard():
            self.log.info("startMonitoringBoard")
            p = select.epoll.fromfd(self._iface.get_fd())
            # add a buffer of 3?
            a = []
            for i in range(5):
                p.poll() # blocks
                event = xwiimote.event()
                self.log.info("after xwiimote event creation")
                self._iface.dispatch(event)
                self.log.info("dispatch event")
                tl = event.get_abs(2)[0]
                a.append(tl)
                self.log.info("published to 'oncounter' with counter {tl}", tl=a)

                #yield self.publish('com.example.oncounter', tl)
                #self.log.info("published to 'oncounter' with counter {counter}",
                 #               counter=tl)

            #return a
        ###
        yield self.register(starMonitoringBoard, 'com.example.balance.monitor')
        self.log.info("procedure starMonitoringBoard() registered")

        def deferredSleep(howLong):
            return deferLater(reactor, howLong, lambda: None)

        @inlineCallbacks
        def publishBalanceData(d):
            self.log.info("printData callback")
            self.log.info(d)
            yield self.publish('com.example.balance.data', d)
            print("published to 'balance.data' with values")

        @inlineCallbacks
        def readBalanceData():
            #self.log.info("readBalanceData")
            fd = self._iface.get_fd()
            self._iface.open(xwiimote.IFACE_BALANCE_BOARD)
            p = poll()
            #self.log.info("p.register called")
            p.register(fd, POLLIN)  

            evt = xwiimote.event()
            tlValues = []
            trValues = []
            brValues = []
            blValues = []
            readValues = {}
            ## this is our buffer of values to read
            ## to average our resolution?
            myCount = 0
            while True:
                #self.log.info("start polling")
                # if self._disconnect == True:
                #     break
                p.poll()
                try:
                    self._iface.dispatch(evt)
                    #self.log.info("dispac")
                    tl = evt.get_abs(2)[0]
                    tr = evt.get_abs(0)[0]
                    br = evt.get_abs(3)[0]
                    bl = evt.get_abs(1)[0]
                    # add sensitivy 3 kg 300
                    #if tl != 0 or tr != 0 or br != 0 or bl != 0:
                    if tl > 300 or tr > 300 or br > 300 or bl > 300:
                    #print(tl)
                    # need to catter for sensitivity

                        tlValues.append(tl/100)
                        trValues.append(tr/100)
                        brValues.append(br/100)
                        blValues.append(bl/100)

                        if myCount == 5:
                            break
                        myCount += 1

                except IOError as e:
                    if e.errno != errno.EAGAIN:
                        print("Bad")

            self._iface.close(xwiimote.IFACE_BALANCE_BOARD)
            #self.log.info("balance values read")
            # if self._disconnect == True:
            #     returnValue(json.dumps("disconnected"))
            # average values and get into readValues
            # this could go into a function ...
            # change to dict
            tlAv = sum(tlValues)/len(tlValues)
            readValues['tl'] = tlAv
            trAv = sum(trValues)/len(trValues)
            readValues['tr'] = trAv
            brAv = sum(brValues)/len(brValues)
            readValues['br'] = brAv
            blAv = sum(blValues)/len(blValues)
            readValues['bl'] = blAv
            readValues['total_weight'] = tlAv + trAv + brAv + blAv


            if len(readValues) == 0:
            #     # how quickly we check again
                yield deferredSleep(0.1)

            else:
                jsonValues = json.dumps(readValues)
                #self.log.info("json values read: ")
                #self.log.info(jsonValues)
                returnValue(jsonValues)

        # PUBLISH and CALL every second .. forever
        #
        counter = 0
        while True:
            # stop sending balance data after disconnect
            # this is needed to get out of the loop and deferred data
            # maybe a better way to do this 
            # if self._disconnect == True:
            #     break

            #self.log.info("inside while loop publish oncounter")
            # PUBLISH an event
            #
            if self._sendBalanceData == True:
                d = readBalanceData()
                d.addCallback(publishBalanceData)
            # else:
            #     break
            
            # if self._sendBalanceData == True:
            #     self.log.info("sendHello true")
            #     # send balance data on via subscription
            #     self.log.info("sendHello true field readBalanceData")
            #     d = readBalanceData()
            #     d.addCallback(printData)
            #     #self.log.info(vals)
            #     #yield self.publish('com.example.oncounter', readBalanceData())
            #     #print("published to 'oncounter' with counter {}".format(counter))
                
            #    counter += 1

            # CALL a remote procedure
            #
                # try:
                #     res = yield self.call('com.example.balance.monitor')
                #     self.log.info("mul2() called lcoally with result: {result}",
                #                   result=res)
                # except ApplicationError as e:
                # # ignore errors due to the frontend not yet having
                # # registered the procedure we would like to call
                #     if e.error != 'wamp.error.no_such_procedure':
                #         raise e
            # control the loop timing?
            yield sleep(1)
