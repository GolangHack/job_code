# coding=utf-8
"""
Восстановление даты после перезагрузки.
"""
import os
import datetime
import time
from pyutils.stopablethread import StopableThread, Singleton
import logging

log = logging.getLogger("date_recovery")


class DateRecovery(StopableThread):
    __metaclass__ = Singleton

    # Период сохранения текущего времени
    UPDATE_PERIOD = 600
    DELAY_PERIOD = 10
    PATH_RECOVER_FILE = "./.date_recovery"

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        super(DateRecovery, self).__init__()
        self._callbackRecovery = None
        self.start(delay=0)

    def _recover(self):
        """Вызываем каллбек восстановления"""
        if self._callbackRecovery:
            self._callbackRecovery()

    def worker(self, *args, **kwargs):
        """Перезаписываем последний файл"""
        current_date = datetime.datetime.now()
        if os.path.isfile(DateRecovery.PATH_RECOVER_FILE):
            with open(DateRecovery.PATH_RECOVER_FILE, "rb") as f:
                date = f.read()
            old_date = datetime.datetime.strptime(date, self.DATETIME_FORMAT)
            delta = current_date - old_date
            delta_seconds = delta.seconds
            # проверка на ошибочность
            if delta_seconds > self.UPDATE_PERIOD + self.DELAY_PERIOD:
                lag = delta_seconds - (self.UPDATE_PERIOD + self.DELAY_PERIOD)
                log.warning("Delta period is not correctly. Lag is %s second. Run recovery callback." % lag)
                self._recover()
        # добавим новую запись
        with open(DateRecovery.PATH_RECOVER_FILE, "wb") as f:
            t = current_date
            f.write(t.strftime(self.DATETIME_FORMAT))
        return self.UPDATE_PERIOD

    def setRecoveryCallback(self, callback):
        """Вызывать функцию в случае непредвиденного обстоятельства"""
        self._callbackRecovery = callback


if __name__ == "__main__":
    DateRecovery()
    while True:
        time.sleep(1)
