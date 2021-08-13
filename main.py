#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Точка входа в приложение"""
print("\033[7m *** PROJECT 'ROBOTCARWASH' TERMINAL ***")
print("\033[0m")

import logging
from logging.handlers import RotatingFileHandler
import os
from PyQt5 import QtCore
import config
import time
import sys
from htmlpy_core import htmlPy
from htmlpy_core.htmlPy.settings import DISABLE
from htmlpy_core.back_end import BackEnd
import scheduler
from vmachine import Vmachine
import data_storage.database.connection_manager as connection_manager
from pyutils.checkInternet import InternetCheckerThread

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_CONFIG_FILE = 'config.conf'

'Грузим настройки подключения к базе данных'

if config.readConfig(PATH_TO_CONFIG_FILE) is None:
    print u"config.conf не был найден. Создайте config.conf и настройки подключения к БД."
else:
    'Инициация подключения к БД'
    connection_manager.initConnection(config.getProperty('database_database'),
                                      host=config.getProperty('database_host'),
                                      password=config.getProperty('database_password'),
                                      user=config.getProperty('database_user'))
    config.readConfigFromCurrentDB()
    'Инициация логов'
    logfile_path_remote = config.getProperty('logfile_path_remote')
    logfile_path_local = config.getProperty('logfile_path_local')

    # Crontab update
    if config.getProperty('is_scheduller_run', default=False, _type="bool"):
        scheduler.initial_report_send(user="pi")
    'Is server is already exist - go firther, else - remount fstab'
    if os.path.isfile(logfile_path_remote + 'iamserver'):
        logfile = logfile_path_remote + 'terminal.log'
    else:
        logfile = logfile_path_local + 'terminal.log'

    formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)21s[%(lineno)3d] %(message)s",
                                  datefmt='%d.%m.%Y %H:%M:%S')
    # Подключить к логгеру обработчик записи логов в файл с ротацией. 10 файлов по 10 мегабайт.
    handlerRFH = RotatingFileHandler(logfile, maxBytes=10000000, backupCount=10)
    handlerRFH.setLevel(logging.INFO)
    handlerRFH.setFormatter(formatter)
    # Возьмем основной логгер, добавим хандлер(ы) куда будут писаться сообщения логгера.
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.propagate = False
    log.addHandler(handlerRFH)


    logging.getLogger(__name__).info('***********************************')
    logging.getLogger(__name__).info('              Startup')
    logging.getLogger(__name__).info('***********************************')
    logging.getLogger(__name__).info('Start load delay timer...')

    load_delay = int(config.getProperty('load_delay'))
    time.sleep(load_delay)
    logging.getLogger(__name__).info('Load delay timer elapsed')

    # check internet every 30 second.
    internet = InternetCheckerThread()

    # Bind app to backend and pass sequencer object to the backend
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Setup application
    app = htmlPy.AppGUI(title=u"Robot washer")
    app.maximized = True
    theme_name = config.getProperty('theme_name', default='default')
    if theme_name == 'default':
        app.template_path = os.path.join(BASE_DIR, "templates/")
        app.static_path = os.path.join(BASE_DIR, "static/")
    else:
        app.template_path = os.path.join(BASE_DIR, "themes/" + str(theme_name) + "/templates/")
        app.static_path = os.path.join(BASE_DIR, "themes/" + str(theme_name) + "/static/")
    app.developer_mode = True
    app.width = 1280
    app.height = 1024
    if config.getProperty('debug_windowed') != "True":
        app.web_app.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
        app.web_app.page().mainFrame().setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        app.window.showFullScreen()
    # полный перехват всех ошибок, чтобы отобразить их в логе
    try:
        be = BackEnd(app)
        vm = Vmachine(be)
        app.text_selection_setting(DISABLE)
        app.bind(be)
        app.start()
    except:
        logging.getLogger(__name__).exception(u'Программа завершилась с ошибкой:')
        raise
