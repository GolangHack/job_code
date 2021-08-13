#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Автоматический поиск и обновление крона для scheduler

Для использования скрипта необходимо убедиться наличие праметра report_time в конфиге
"""


import logging
import os
import config
try:
    from crontab import CronTab
except ImportError:
    logging.getLogger(__name__).critical(u"Library 'crontab' was not found. Install it: pip install crontab")
    import sys
    sys.exit()

# пометка прямо в кронтабе
id = "sendRaportToBoss"


def initial_report_send(user="pi"):
    log = logging.getLogger("crontabUpdate")
    log.setLevel(logging.DEBUG)

    report_hour, report_minutes = config.getProperty('report_time', '9:00').split(":")
    try:
        cron = CronTab(user=user)
    except IOError:
        log.error(u"Нужно указать пользователя в этой функции, под котором был запущен скрипт с правами root")
        log.critical(u"Scheduler was not started. Report will not sended")
        return
    for job in cron:
        if job.comment == id:
            log.info(u"Удаление задачи из crontab: " + str(job))
            cron.remove(job)
            cron.write()
    job = cron.new(command='cd '+os.path.dirname(os.path.abspath(__file__))+' && DISPLAY=:0 ./main.py',
                   comment='sendRaportToBoss')
    job.minute.on(report_minutes)
    job.hour.on(report_hour)
    log.info(u"Создана задача " + str(job))
    cron.write()


if __name__ == '__main__':
    logging.basicConfig()
    # для HOT UPDATE
    config.readConfig("../config.conf")
    fileName = config.getProperty('config_name')
    config.readConfig("../"+fileName)
    initial_report_send(user="pi")