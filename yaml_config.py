#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from os.path import *

import yaml


class YamlConfig(object):

    def __init__(self, source):
        self.log = logging.getLogger(__name__)
        with open(abspath(join(dirname(__file__), source))) as f:
            self.__config = yaml.safe_load(f)

    def get(self, section, property):
        try:
            return self.__config[section][property]
        except KeyError:
            self.log.error("Property '{p}' or section {s} not found!"
                           .format(p=property, s=section))
            return None
