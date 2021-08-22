# -*- coding: utf-8 -*-

import inspect
import ctypes
import xml.dom.minidom
import sys, platform, os

class DTO9Base(object):

    DEFAULT_BUFF_SIZE = 4096
    CREATE_INTERFACE_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_int)
    RELEASE_INTERFACE_PROTOTYPE = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_void_p))
    SET_INT_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int)
    GET_INT_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    SET_DOUBLE_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_double)
    GET_DOUBLE_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_double))
    SET_BUFF_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_wchar_p)
    GET_BUFF_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int)
    SET_BUFF_BY_KEY_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p)
    GET_BUFF_BY_KEY_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p,
                                                 ctypes.c_int)
    SET_VOIDPTR_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    GET_VOIDPTR_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    METHOD_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

    def __init__(self, library_name, version):#инициализация класса
        self.library_name = library_name#имя библиотеки
        assert sys.version_info >= (2, 6)
        if platform.system() == 'Windows':
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'libgcc_s_dw2-1.dll', 
            mode=ctypes.RTLD_LOCAL)
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'mingwm10.dll', 
            mode=ctypes.RTLD_LOCAL)
        self.library = ctypes.CDLL(self.library_name, mode=ctypes.RTLD_LOCAL)
        func = self.CREATE_INTERFACE_PROTOTYPE(('Create{}Interface'.format(self._module_name()), 
        self.library))#создаем прототип интерфэйса
        self.interface = ctypes.c_void_p(func(version))

    def __del__(self):
        func = self.RELEASE_INTERFACE_PROTOTYPE(('Release{}Interface'.format(self._module_name()), 
        self.library))
        func(ctypes.pointer(self.interface))
        
    def _to_string(self, value): 
        if sys.version_info[0] < 3:
            return unicode(value)
        else:
            return str(value)

    def _module_name(self):
        return 'Base'

    def _settingsVersion(self):
        return 1

    def _print_result(self, name):
        s = '%s: [%d]' % (name, self.get_ResultCode())
        print(s)

    def _getter_name(self, prop):
        return 'get_%s' % prop

    def _setter_name(self, prop):
        return 'put_%s' % prop

    def _get_int(self, prop):
        func = self.GET_INT_PROTOTYPE((self._getter_name(prop), self.library))
        value = ctypes.c_int(0)
        func(self.interface, ctypes.pointer(value))
        return value.value

    def _set_int(self, prop, value):
        func = self.SET_INT_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_int(int(value))) < 0:
            return None
        return 0

    def _get_double(self, prop):
        func = self.GET_DOUBLE_PROTOTYPE((self._getter_name(prop), self.library))
        value = ctypes.c_double(0.0)
        func(self.interface, ctypes.pointer(value))
        return value.value

    def _set_double(self, prop, value):
        func = self.SET_DOUBLE_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_double(float(value))) < 0:
            return None
        return 0

    def _get_bool(self, prop):
        func = self.GET_INT_PROTOTYPE((self._getter_name(prop), self.library))
        value = ctypes.c_int(0)
        func(self.interface, ctypes.pointer(value))
        return False if not value.value else True

    def _set_bool(self, prop, value):
        func = self.SET_INT_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_int(bool(value))) < 0:
            return None
        return 0

    def _get_void_ptr(self, prop):
        func = self.GET_VOIDPTR_PROTOTYPE((self._getter_name(prop), self.library))
        ptr = ctypes.c_void_p(0)
        func(self.interface, ctypes.pointer(ptr))
        return ptr.value

    def _set_void_ptr(self, prop, ptr):
        func = self.SET_VOIDPTR_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_void_p(ptr)) < 0:
            return None
        return 0

    def _get_buff(self, prop):
        func = self.GET_BUFF_PROTOTYPE((self._getter_name(prop), self.library))
        buff = ctypes.create_unicode_buffer(self.DEFAULT_BUFF_SIZE)
        size = func(self.interface, buff, self.DEFAULT_BUFF_SIZE)
        if size > self.DEFAULT_BUFF_SIZE:
            buff = ctypes.create_unicode_buffer(size)
            size = func(self.interface, buff, size)
        if size < 0:
            return None

        return buff.value

    def _set_buff(self, prop, buff):
        func = self.SET_BUFF_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_wchar_p(unicode(buff))) < 0:
            return None
        return 0

    def _get_buff_by_key(self, prop, name):
        func = self.GET_BUFF_BY_KEY_PROTOTYPE((self._getter_name(prop), self.library))
        buff = ctypes.create_unicode_buffer(self.DEFAULT_BUFF_SIZE)
        size = func(self.interface, ctypes.c_wchar_p(self._to_string(name)), buff, self.DEFAULT_BUFF_SIZE)
        if size > self.DEFAULT_BUFF_SIZE:
            buff = ctypes.create_unicode_buffer(size)
            size = func(self.interface, ctypes.c_wchar_p(self._to_string(name)), buff, size)
        if size < 0:
            return None

        return buff.value

    def _set_buff_by_key(self, prop, name, buff):
        func = self.SET_BUFF_BY_KEY_PROTOTYPE((self._setter_name(prop), self.library))
        if func(self.interface, ctypes.c_wchar_p(self._to_string(name)), ctypes.c_wchar_p(self._to_string(buff))) < 0:
            return None
        return 0

    def _exec_method(self, name):
        func = self.METHOD_PROTOTYPE((name, self.library))
        if func(self.interface) < 0:
            return None
        return 0

    def get_Result(self):
        return self.get_ResultCode(), self.get_ResultDescription(), self.get_BadParam(), self.get_BadParamDescription()

    def get_LicenseValid(self):
        return self._get_int('LicenseValid')

    def get_LicenseExpiredDate(self):
        return self._get_buff('LicenseExpiredDate')

    def get_Version(self):
        return self._get_buff('Version')

    def get_DriverName(self):
        return self._get_buff('DriverName')

    def get_ResultCode(self):
        return self._get_int('ResultCode')

    def get_ResultDescription(self):
        return self._get_buff('ResultDescription')

    def get_BadParam(self):
        return self._get_int('BadParam')

    def get_BadParamDescription(self):
        return self._get_buff('BadParamDescription')

    def get_DeviceEnabled(self):
        return self._get_bool('DeviceEnabled')

    def put_DeviceEnabled(self, value):
        if self._set_bool('DeviceEnabled', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ApplicationHandle(self):
        return self._get_void_ptr('ApplicationHandle')

    def put_ApplicationHandle(self, value):
        if self._set_void_ptr('ApplicationHandle', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DeviceSettings(self):
        settings = self._get_buff('DeviceSettings')
        if settings is None:
            self._print_result(inspect.currentframe().f_code.co_name)
            return None
        else:
            result = dict()
            for el in xml.dom.minidom.parseString(settings).getElementsByTagName('value'):
                setting_name = el.getAttribute('name')
                setting_value = []
                for child in el.childNodes:
                    if child.nodeType == child.TEXT_NODE:
                        setting_value.append(child.data)
                setting_value = ''.join(setting_value)
                result[setting_name] = setting_value
            return result

    def put_DeviceSettings(self, settings):
        settings_xml = xml.dom.minidom.Document()
        version = self._settingsVersion()
        root = settings_xml.createElement('settings')
        root.setAttribute('version', self._to_string(version))
        settings_xml.appendChild(root)
        for name, value in settings.items():
            setting_node = settings_xml.createElement('value')
            setting_node.setAttribute('name', name)
            setting_node.appendChild(settings_xml.createTextNode(self._to_string(value)))
            root.appendChild(setting_node)
        if self._set_buff('DeviceSettings', settings_xml.toxml()) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DeviceSingleSetting(self, name):
        return self._get_buff_by_key('DeviceSingleSettingAsBuff', name)

    def put_DeviceSingleSetting(self, name, value):
        if self._set_buff_by_key('DeviceSingleSettingAsBuff', name, value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DeviceSingleSettingMapping(self, name):
        value = self._get_buff_by_key('DeviceSingleSettingMapping', name)
        if value is None:
            self._print_result(inspect.currentframe().f_code.co_name)
            return None
        else:
            result = dict()
            for pair in value.split(';'):
                if pair:
                    [_key, _value] = pair.split(':', 1)
                    result[_key] = _value
            return result

    def ApplySingleSettings(self):
        if self._exec_method('ApplySingleSettings') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ResetSingleSettings(self):
        if self._exec_method('ResetSingleSettings') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ShowProperties(self):
        if platform.system() == 'Windows':
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'QtCore4.dll', mode=ctypes.RTLD_LOCAL)
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'QtGui4.dll', mode=ctypes.RTLD_LOCAL)
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'QtXml4.dll', mode=ctypes.RTLD_LOCAL)
            ctypes.CDLL(os.path.dirname(self.library_name) + os.sep + 'QtNetwork4.dll', mode=ctypes.RTLD_LOCAL)
        if self._exec_method('ShowProperties') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()
