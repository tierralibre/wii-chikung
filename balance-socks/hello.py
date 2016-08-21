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

from twisted.internet.defer import inlineCallbacks
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
            global sendHello
            global _iface
            self.log.info("wait for balance board received: {x} and {y}", x=x, y=y)
            mon = xwiimote.monitor(True, False)
            dev = None
            conn = False
            counter = 0
            self.log.info("before wait for balance while loop" )
            while True:
                mon.get_fd(True) # blocks
                connected = mon.poll()
                self.log.info("in for balance while loop" )

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
                        self.log.info("found balance board" )
                        self._iface = iface
                        counter = "Board Found"
                        self._sendBalanceData = True
                        break
                    
            #return true
            return counter
        ###
        yield self.register(wait_for_balanceboard, 'com.example.balance')
        self.log.info("procedure wait_for_balanceboard() registered")
        ###

        def disconnect_balanceboard():
            self.log.info("closing device iface")
            self._iface.close(xwiimote.IFACE_BALANCE_BOARD)
            self.log.info("bt disconnect device")
            subprocess.call(["bt-device", "-d", "Nintendo RVL-WBC-01"])
            self._sendBalanceData = False
            return "Done"

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

        def readBalanceData():
            self.log.info("readBalanceData")
            fd = self._iface.get_fd()
            self._iface.open(xwiimote.IFACE_BALANCE_BOARD)
            p = poll()
            self.log.info("p.register called")
            p.register(fd, POLLIN)  

            evt = xwiimote.event()
            eadValues = []
            myCount = 0
            while True:
                self.log.info("start polling")
                p.poll()
                try:
                    self._iface.dispatch(evt)
                    tl = evt.get_abs(2)[0]
                    if tl != 0:
                    #print(tl)
                        readValues.append(tl)
                        if myCount == 5:
                            break
                        myCount += 1

                except IOError as e:
                    if e.errno != errno.EAGAIN:
                        print("Bad")

            self._iface.close(xwiimote.IFACE_BALANCE_BOARD)
            self.log.info("balance values read")
            jsonValues = json.dumps(readValues)
            self.log.info(jsonValues)
            returnValue(jsonValues)

        # PUBLISH and CALL every second .. forever
        #
        counter = 0
        while True:
            #self.log.info("inside while loop publish oncounter")
            # PUBLISH an event
            #
            if self._sendBalanceData == True:
                self.log.info("sendHello true")
                # send balance data on via subscription
                vals = yield readBalanceData()
                self.log.info(vals)
                yield self.publish('com.example.oncounter', readBalanceData())
                print("published to 'oncounter' with counter {}".format(counter))
                
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

            yield sleep(1)
