#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from Queue import Queue, Empty


class DelayedExecution(threading.Thread):#потоки

    def __init__(self, ):
        threading.Thread.__init__(self)
        self.q = Queue()#очередь
        self.daemon = True#демон
        self.executing = False#изменнеия 
        self.start()#старат

    def restart(self, delay, action, *args):#перезапуск 
        self.args = args
        self.action = action
        self.q.put(delay)

    def cancel(self):#закрытие
        delay = None#задержка
        self.q.put(delay)#добавить в очередь задержку

    def isExecuting(self):
        return self.executing#изменеие

    def run(self):#запуск
        delay = None#задержка
        '''
        пока справдливо условие попытаться вернуть задержку
        в противном случае вывести ее в значение None
        '''
        while True:
            try:
                delay = self.q.get(True, delay)
                self.executing = True
            except Empty as e:
                # print self.args
                self.action(self.args)
                self.executing = False
                delay = None


