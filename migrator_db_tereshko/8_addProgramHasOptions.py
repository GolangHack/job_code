#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

sys.path.append('../')

from data_storage.database import connection_manager
from data_storage.database import models_generated as db
from uuid import uuid4 as uuid
import config


def _getGroupByName(name):
    try:
        return db.VariableGroup.get(db.VariableGroup.name == name)
    except db.VariableGroup.DoesNotExist:
        variableGroup = db.VariableGroup(
            id=uuid(),
            name=name,
            description="Автоматически сгенерированная группа.")
        variableGroup.save(force_insert=True)
        return variableGroup


def _initConnection():
    connection_manager.initConnection(
        dbName=config.getProperty('database_database'),
        host=config.getProperty('database_host'),
        user=config.getProperty('database_user'),
        password=config.getProperty('database_password'))


def _getPrograms():
    return (db.Program
            .select()
            .where(db.Program.program_type == 0))


def _createProgramHasOptionsVariables():
    for program in _getPrograms():
        var_id = uuid()
        db.Variable.create(
            id=var_id,
            name='_'.join(['program', str(program.number), 'HasOptions']),
            value=True,
            default_value=True,
            type='bool',
            description='Доступность дополнительных опций',
            modifiable="1",
            variable_group=_getGroupByName('ProgramPrice'))

        db.ProgramHasVariable.create(
            id=uuid(),
            program=program.id,
            variable=var_id)


if __name__ == '__main__':
    if config.readConfig('../config.conf'):
        _initConnection()
        _createProgramHasOptionsVariables()
        print(u'Миграция успешно выполнена.')
    else:
        print(u'Файл config.conf с настройками подключения к БД '
              u'не был найден. Создайте файл и повторите попытку.')
