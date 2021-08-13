#!/usr/bin/env python

class WriteUnit:
    def __init__(self, unit_a, reg_a, count, data):
        self._unit_a = unit_a
        self._reg_a = reg_a
        self._count = count
        self._data = data

    def getUnit(self):
        return self._unit_a

    def getAddr(self):
        return self._reg_a

    def getCount(self):
        return self._count

    def getData(self):
        return self._data

    def __str__(self):
        return 'adr: ' + str(self._unit_a) + ' reg_adr: ' + str(self._reg_a) +\
             ' count: ' + str(self._count) + ' data: ' + str(self._data)
