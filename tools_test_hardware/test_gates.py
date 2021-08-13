#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестирование ворот, главное знать пины ворот
Created by treeloys at 21.07.20
"""
TEST = False

import argparse
import threading
import sys
sys.path.insert(0, "../")

if not TEST:
    from rplclib.rplc import RaspeoPLC
from gates import Gates



parser = argparse.ArgumentParser(description=u"Тестирование ворот")
parser.add_argument("-rv", "--rplc_version", type=int, default=2, help=u"Версия RPLC")
parser.add_argument("-i", "--impulse", type=int, default=10, help=u"Время ипульса")
"Адрес ворота"
parser.add_argument("-p", "--pin", type=int, help=u"Pin ворот")
parser.add_argument("-m", "--module", type=int, default=0, help=u"модуль ворот")
"Управляющие"
parser.add_argument("-o", "--open", help=u"Открыть ворота", action='store_true')
parser.add_argument("-c", "--close", help=u"Закрыть ворота", action='store_true')
parser.add_argument("-state", "--state", help=u"Состояния ворот (открыто/закрыто)", action='store_true')
arg = parser.parse_args()

if not TEST:
    rplc = RaspeoPLC(version=arg.rplc_version)
else:
    rplc = None


def openGatesHandler():
    print("Open exit gate impulse")

    def disOpenContact():
        rplc.module[arg.module].setOutput(arg.pin, False)

    threading.Timer(arg.impulse, disOpenContact).start()
    rplc.module[arg.module].setOutput(arg.pin, True)


def closeGatesHandler():
    print("Close exit gate impulse")

    def disCloseContact():
        rplc.module[arg.module].setOutput(arg.pin, False)

    threading.Timer(arg.impulse, disCloseContact).start()
    rplc.module[arg.module].setOutput(arg.pin, True)


gate = Gates("Testing gate")
gate.registerOpenGatesHandler(openGatesHandler)
gate.registerCloseGatesHandler(closeGatesHandler)


if __name__ == "__main__":
    "Проверка на наличие пина"
    if arg.pin is not None:
        print(u"Настройки ворот: версия rplc={}, модуль={}, пин={}, импуль={};".format( arg.rplc_version,
                                                                                       arg.module,
                                                                                       arg.pin,
                                                                                       arg.impulse))
        if arg.open:
            gate.openGates()
        elif arg.close:
            gate.closeGates()
        elif arg.state:
            if gate.isGatesOpened():
                print(u"Статус ворот: Ворота открыты")
            else:
                print(u"Статус ворот: Ворота закрыты")
    else:
        print(u"Используй -h аргумент")
