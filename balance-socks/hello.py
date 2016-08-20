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
import select
import subprocess

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
                    if iface.get_devtype() == 'balanceboard':
                        #yield self.publish('com.example.oncounter', "balanceBoard connected")
                        self.log.info("found balance board" )
                        self._iface = iface
                        counter = "Board Found"
                        sendHello = True
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
            return "Done"

        yield self.register(disconnect_balanceboard, 'com.example.balance.disconnect')
        self.log.info("procedure disconnect_balanceboard() registered")
        ####

        ###

        # PUBLISH and CALL every second .. forever
        #
        counter = 0
        while True:
            #self.log.info("inside while loop publish oncounter")
            # PUBLISH an event
            #
            if sendHello == True:
                self.log.info("sendHello true")
                yield self.publish('com.example.oncounter', counter)
                self.log.info("published to 'oncounter' with counter {counter}",
                            counter=counter)
                counter += 1

            # CALL a remote procedure
            #
            # try:
            #     res = yield self.call('com.example.mul2', counter, 3)
            #     self.log.info("mul2() called lcoally with result: {result}",
            #                   result=res)
            # except ApplicationError as e:
            #     # ignore errors due to the frontend not yet having
            #     # registered the procedure we would like to call
            #     if e.error != 'wamp.error.no_such_procedure':
            #         raise e

            yield sleep(1)
