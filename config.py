#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import configparser
import logging
import os
from data_storage.database.settingsManager import SettingChangedReceiver, SettingsManager
from data_storage.database.connection_manager import initConnection
log = logging.getLogger(__name__)

configuration = None
ETHERNET = 'eth0'


class VariablesFromDB(SettingChangedReceiver):
    """В данной реализации нету автоупдейта"""

    def settingChanged(self, setting):
        pass

    def __init__(self):
        self.sm = SettingsManager()
        self.settings = self.sm.getSettingsAll()
        self.groupedSettings = self.sm.getSettingsGroupAll()

        # TODO как-то реализовать подписку на параметры
        # for key in self.settings:
        #     self.sm.subscribeByName(self, self.settings[key])

    'эмуляция интерфейса configparser'

    def sections(self):
        return [x for x in self.groupedSettings]

    def has_option(self, sec, pname, prefix):
        return self.settings.has_key(prefix+pname)

    def has_type(self, sec, pname, prefix):
        return True if self.settings[prefix+pname].getNameType() != "" else False

    def get(self, sec, pname, prefix):
        return self.settings[prefix+pname].getValue()

    def items(self, sections):
        return [(x, self.groupedSettings[sections][x].getValue()) for x in self.groupedSettings[sections]]

def readConfig(f_name):
    if not os.path.exists(f_name):
        log.critical(u'По указанному пути "%s" нет файла конфигурации', f_name)
        return None
    global configuration
    configuration = configparser.RawConfigParser()
    log.info(u'Загружен файл конфигурации по пути %s', f_name)
    configuration.read(f_name)
    return True

def _typing(value, nametype):
        # Преобразование входящего с текстовым типом в значение python
        if nametype == 'bool':
            a_e = value
            return (a_e == 'True') | (a_e == 'true') | (a_e == '1')
        elif nametype == 'int':
            return int(value)
        elif nametype == 'float':
            return float(value)
        elif nametype == 'json':
            return json.loads(value)
        elif nametype == 'jsonarray':
            return json.loads(value)["array"]
        elif nametype == 'str' or nametype == '' or nametype == 'string':
            return value
        else:
            raise Exception('Variable type with not founded %s' % nametype)

def getProperty(pname, default=None, _type=None, prefix="cfg_"):
    """
    Получить параметр из текущего конфига, используя config.conf
    :param pname: - имя параметра
    :param default: - значение параметра по умолчанию
    :param _type: - в какое значение преобразовать 'bool', 'int', 'float', 'json'. В случае None - str
    :param prefix: - какой использовать префикс в имени переменной
    :return: параметр
    """
    "It db property? "
    if type(configuration) == VariablesFromDB:
        if configuration.has_option("", pname, prefix):
            "No has_type? Update data_storage!"
            if configuration.has_type("", pname, prefix) or not _type:
                return configuration.get("", pname, prefix)
            else:
                return _typing(configuration.get("", pname, prefix), _type)

    else:
        for sec in configuration.sections():
            if configuration.has_option(sec, pname):
                value = configuration.get(sec, pname)
                if _type:
                    return _typing(value, _type)
                else:
                    return configuration.get(sec, pname)
    if default is not None:
        log.warning("Property %s does not exist in properties. But exist default. Set: %s", pname, default)
        return default
    log.critical('Property %s does not exist. Return None.', pname)
    return None


def setProperty(name, value):
    """Устанавливает значение в базе данных значение variable"""
    global configuration
    if isinstance(configuration, VariablesFromDB):
        configuration.settings[name].setValue(value)
        log.info('Set "%s" value "%s"' % (name, value))
    else:
        log.info('Never set property "%s" becouse it only db setter' % name)

def getConfiguration():
    return configuration


'Работа с базой данных'


def readConfigFromCurrentDB():
    global configuration
    log.debug(u"Старт загрузки конфигурации из БД")
    configuration = VariablesFromDB()
    log.info(u'Загружены настройки конфигурации с базы данных')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    readConfig("config.conf")
    print("config_name property", getProperty("config_name", _type="bool"))
    initConnection(getProperty('database_database'),
                                 host=getProperty('database_host'),
                                 password=getProperty('database_password'),
                                 user=getProperty('database_user'))
    readConfigFromCurrentDB()
    print("Property atol_version", getProperty("atol_version"))