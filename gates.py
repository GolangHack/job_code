#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from itertools import chain

class GatesStub(object):
    def __init__(self,  \
                 description='GateStub '):
        self.description = description
        self.gatesOpened = False

    def registerOpenGatesHandler(self, handler, *args, **kwargs):
        pass

    def registerCloseGatesHandler(self, handler, *args, **kwargs):
        pass

    def openGates(self, *args, **kwargs):
        logging.getLogger(__name__).info(self.description + " Open")
        self.gatesOpened = True

    def closeGates(self, *args, **kwargs):
        logging.getLogger(__name__).info(self.description + " Close")
        self.gatesOpened = False

    def isGatesOpened(self):
        return self.gatesOpened

class Gates(object):

    def __init__(self,  \
                 description='Gate ' \
                 ):
        self._log = logging.getLogger(__name__)
        self.description = description
        self.gatesOpened = False
        self.openGatesHandler = None
        self.closeGatesHandler = None
        self._close_args = []
        self._close_kwargs = {}
        self._open_args = []
        self._open_kwargs = {}
        self._log.info("{} initialized".format(description))

    def registerOpenGatesHandler(self, handler, *args, **kwargs):
        self._open_args = args
        self._open_kwargs = kwargs
        self.openGatesHandler = handler
        self._log.debug("{} open gate handler registered".format(self.description))

    def registerCloseGatesHandler(self, handler, *args, **kwargs):
        self._close_args = args
        self._close_kwargs = kwargs
        self.closeGatesHandler = handler
        self._log.debug("{} close gate handler registered".format(self.description))

    def openGates(self, *args, **kwargs):
        self._log.info("{} open".format(self.description))
        _args = list(chain(args, self._open_args))
        kwargs.update(self._open_kwargs)
        self.gatesOpened = True
        if self.openGatesHandler is not None:
            self.openGatesHandler(*_args, **kwargs)

    def closeGates(self, *args, **kwargs):
        self._log.info("{} close".format(self.description))
        _args = list(chain(args, self._open_args))
        kwargs.update(self._close_kwargs)
        self.gatesOpened = False
        if self.closeGatesHandler is not None:
            self.closeGatesHandler(*_args, **kwargs)

    def isGatesOpened(self):
        return self.gatesOpened
