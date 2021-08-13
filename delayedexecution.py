#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from Queue import Queue, Empty


class DelayedExecution(threading.Thread):

    def __init__(self, ):
        threading.Thread.__init__(self)
        self.q = Queue()
        self.daemon = True
        self.executing = False
        self.start()

    def restart(self, delay, action, *args):
        self.args = args
        self.action = action
        self.q.put(delay)

    def cancel(self):
        delay = None
        self.q.put(delay)

    def isExecuting(self):
        return self.executing

    def run(self):
        delay = None
        while True:
            try:
                delay = self.q.get(True, delay)
                self.executing = True
            except Empty as e:
                # print self.args
                self.action(self.args)
                self.executing = False
                delay = None


