#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by treeloys at 2.05.20

Добавление нужных переменных

"""
import sys
sys.path.append('../')
from data_storage.database import connection_manager
from data_storage.database import models_generated as db

import config
from uuid import uuid4 as uuid

PATH_TO_CONFIG_FILE = '../config.conf'

def getGroupByName(sectionname):
    """Получить группу по имени. Если ее нет, сгенерить и заретурнить, если есть, просто отдать ее"""
    try:
        return db.VariableGroup.get(db.VariableGroup.name == sectionname)
    except db.VariableGroup.DoesNotExist:
        vg = db.VariableGroup(id=uuid(), name=sectionname, description="Автоматически сгенерированная группа.")
        vg.save(force_insert=True)
        return vg

'Грузим настройки подключения к базе данных'

if config.readConfig(PATH_TO_CONFIG_FILE) is None:
    print u"config.conf не был найден. Создайте config.conf и настройки подключения к БД."
else:
    'Инициация подключения к БД'
    connection_manager.initConnection(config.getProperty('database_database'),
                                      host=config.getProperty('database_host'),
                                      password=config.getProperty('database_password'),
                                      user=config.getProperty('database_user'))
    group_general = getGroupByName("general")
    db.Variable.create(id=uuid(),
                         name="defcardprop_request_enter_phone_enabled",
                         value="True",
                         default_value="True",
                         type="bool",
                         description="Параметр по умолчанию, если человек выбрал больше не спрашивать привязку номера",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="defcardprop_adw_enabled",
                         value="True",
                         default_value="True",
                         type="bool",
                         description="Параметр по умолчанию - если выбрали показывать рекламу",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_license_text_personal_data_processing",
                         value="Текст соглашения на обработку персональных данных",
                         default_value="Текст соглашения на обработку персональных данных",
                         type="",
                         description="Текст соглашения на обработку персональных данных",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_license_text_adw_data_agreement",
                         value="Текст соглашения на рассылку данных",
                         default_value="Текст соглашения на рассылку данных",
                         type="",
                         description="Текст соглашения на рассылку данных",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_requestPhoneForClientCardEnabled",
                         value="True",
                         default_value="True",
                         type="bool",
                         description="Запрашивать ли после поднесения карты привязку номера телефона",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_enable_sms_gate_pin_code",
                         value="False",
                         default_value="False",
                         type="bool",
                         description="Включить отправку сообщений?",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_sms_gate_login",
                         value="",
                         default_value="",
                         type="",
                         description="Указать логин для смс шлюза",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_sms_gate_password",
                         value="",
                         default_value="",
                         type="",
                         description="Указать логин для смс шлюза",
                         modifiable="1",
                         variable_group=group_general)
    db.Variable.create(id=uuid(),
                         name="cfg_sms_gate_host",
                         value="",
                         default_value="",
                         type="",
                         description="Указать хост смс шлюза",
                         modifiable="1",
                         variable_group=group_general)


if __name__ == "__main__":
    print u'Миграция выполнена'
    print u'Необходимо переключить значения переменных для sms_gate_login, sms_gate_password, cfg_enable_sms_gate_pin_code для работы сообщений'