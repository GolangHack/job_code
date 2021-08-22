# -*- coding: utf-8 -*-

import dto9base
import ctypes
import inspect


class Fptr(dto9base.DTO9Base):
    callback = None
    SET_TRIPLE_INT_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int,
                                                ctypes.c_void_p,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int)
    GET_TRIPLE_INT_PROTOTYPE = ctypes.CFUNCTYPE(ctypes.c_int,
                                                ctypes.c_void_p,
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int),
                                                ctypes.POINTER(ctypes.c_int))

    def _module_name(self):
        return 'Fptr'

    def _settingsVersion(self):
        return 4

    def get_Caption(self):
        return self._get_buff('Caption')

    def put_Caption(self, value):
        if self._set_buff('Caption', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CaptionPurpose(self):
        return self._get_int('CaptionPurpose')

    def put_CaptionPurpose(self, value):
        if self._set_int('CaptionPurpose', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CaptionIsSupported(self):
        return self._get_bool('CaptionIsSupported')

    def get_CaptionName(self):
        return self._get_buff('CaptionName')

    def get_Value(self):
        return self._get_double('Value')

    def put_Value(self, value):
        if self._set_double('Value', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ValuePurpose(self):
        return self._get_int('ValuePurpose')

    def put_ValuePurpose(self, value):
        if self._set_int('ValuePurpose', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ValueIsSupported(self):
        return self._get_bool('ValueIsSupported')

    def get_ValueName(self):
        return self._get_buff('ValueName')

    def get_ValueMapping(self):
        value = self._get_buff('ValueMapping')
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

    def get_CharLineLength(self):
        return self._get_int('CharLineLength')

    def get_SerialNumber(self):
        return self._get_buff('SerialNumber')

    def put_SerialNumber(self, value):
        if self._set_buff('SerialNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Date(self):
        func = self.GET_TRIPLE_INT_PROTOTYPE((self._getter_name('Date'), self.library))
        year = ctypes.c_int(0)
        month = ctypes.c_int(0)
        day = ctypes.c_int(0)
        func(self.interface, ctypes.pointer(day), ctypes.pointer(month), ctypes.pointer(year))
        return [day.value, month.value, year.value]

    def put_Date(self, date):
        func = self.SET_TRIPLE_INT_PROTOTYPE((self._setter_name('Date'), self.library))
        func(self.interface, ctypes.c_int(date[0]), ctypes.c_int(date[1]), ctypes.c_int(date[2]))
        return self.get_Result()

    def get_Time(self):
        func = self.GET_TRIPLE_INT_PROTOTYPE((self._getter_name('Time'), self.library))
        hour = ctypes.c_int(0)
        minute = ctypes.c_int(0)
        second = ctypes.c_int(0)
        func(self.interface, ctypes.pointer(hour), ctypes.pointer(minute), ctypes.pointer(second))
        return [hour.value, minute.value, second.value]

    def put_Time(self, time):
        func = self.SET_TRIPLE_INT_PROTOTYPE((self._setter_name('Time'), self.library))
        if func(self.interface, ctypes.c_int(time[0]), ctypes.c_int(time[1]), 
        ctypes.c_int(time[2])) < 0:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Fiscal(self):
        return self._get_bool('Fiscal')

    def get_TestMode(self):
        return self._get_bool('TestMode')

    def put_TestMode(self, value):
        if self._set_bool('TestMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_EnableCheckSumm(self):
        return self._get_bool('EnableCheckSumm')

    def put_EnableCheckSumm(self, value):
        if self._set_bool('EnableCheckSumm', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_UserPassword(self):
        return self._get_buff('UserPassword')

    def put_UserPassword(self, value):
        if self._set_buff('UserPassword', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Mode(self):
        return self._get_int('Mode')

    def put_Mode(self, value):
        if self._set_int('Mode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Alignment(self):
        return self._get_int('Alignment')

    def put_Alignment(self, value):
        if self._set_int('Alignment', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TextWrap(self):
        return self._get_int('TextWrap')

    def put_TextWrap(self, value):
        if self._set_int('TextWrap', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Barcode(self):
        return self._get_buff('Barcode')

    def put_Barcode(self, value):
        if self._set_buff('Barcode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeType(self):
        return self._get_int('BarcodeType')

    def put_BarcodeType(self, value):
        if self._set_int('BarcodeType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PrintBarcodeText(self):
        return self._get_bool('PrintBarcodeText')

    def put_PrintBarcodeText(self, value):
        if self._set_bool('PrintBarcodeText', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_SlipDocOrientation(self):
        return self._get_int('SlipDocOrientation')

    def put_SlipDocOrientation(self, value):
        if self._set_int('SlipDocOrientation', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Scale(self):
        return self._get_double('Scale')

    def put_Scale(self, value):
        if self._set_double('Scale', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Height(self):
        return self._get_int('Height')

    def put_Height(self, value):
        if self._set_int('Height', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TypeClose(self):
        return self._get_int('TypeClose')

    def put_TypeClose(self, value):
        if self._set_int('TypeClose', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Summ(self):
        return self._get_double('Summ')

    def put_Summ(self, value):
        if self._set_double('Summ', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CheckType(self):
        return self._get_int('CheckType')

    def put_CheckType(self, value):
        if self._set_int('CheckType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CheckState(self):
        return self._get_int('CheckState')

    def get_CheckNumber(self):
        return self._get_int('CheckNumber')

    def put_CheckNumber(self, value):
        if self._set_int('CheckNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_RegisterNumber(self):
        return self._get_int('RegisterNumber')

    def put_RegisterNumber(self, value):
        if self._set_int('RegisterNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DocNumber(self):
        return self._get_int('DocNumber')

    def put_DocNumber(self, value):
        if self._set_int('DocNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_SessionOpened(self):
        return self._get_bool('SessionOpened')

    def get_Session(self):
        return self._get_int('Session')

    def put_Session(self, value):
        if self._set_int('Session', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CheckPaperPresent(self):
        return self._get_bool('CheckPaperPresent')

    def get_ControlPaperPresent(self):
        return self._get_bool('ControlPaperPresent')

    def get_PLUNumber(self):
        return self._get_int('PLUNumber')

    def put_PLUNumber(self, value):
        if self._set_int('PLUNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Name(self):
        return self._get_buff('Name')

    def put_Name(self, value):
        if self._set_buff('Name', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Price(self):
        return self._get_double('Price')

    def put_Price(self, value):
        if self._set_double('Price', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Quantity(self):
        return self._get_double('Quantity')

    def put_Quantity(self, value):
        if self._set_double('Quantity', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Department(self):
        return self._get_int('Department')

    def put_Department(self, value):
        if self._set_int('Department', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DiscountType(self):
        return self._get_int('DiscountType')

    def put_DiscountType(self, value):
        if self._set_int('DiscountType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReportType(self):
        return self._get_int('ReportType')

    def put_ReportType(self, value):
        if self._set_int('ReportType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BufferedPrint(self):
        return self._get_bool('BufferedPrint')

    def put_BufferedPrint(self, value):
        if self._set_bool('BufferedPrint', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_InfoLine(self):
        return self._get_buff('InfoLine')

    def get_Model(self):
        return self._get_int('Model')

    def get_ClearFlag(self):
        return self._get_bool('ClearFlag')

    def put_ClearFlag(self, value):
        if self._set_bool('ClearFlag', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileName(self):
        return self._get_buff('FileName')

    def put_FileName(self, value):
        if self._set_buff('FileName', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_INN(self):
        return self._get_buff('INN')

    def put_INN(self, value):
        if self._set_buff('INN', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_MachineNumber(self):
        return self._get_buff('MachineNumber')

    def put_MachineNumber(self, value):
        if self._set_buff('MachineNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_License(self):
        return self._get_buff('License')

    def put_License(self, value):
        if self._set_buff('License', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_LicenseNumber(self):
        return self._get_int('LicenseNumber')

    def put_LicenseNumber(self, value):
        if self._set_int('LicenseNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Table(self):
        return self._get_int('Table')

    def put_Table(self, value):
        if self._set_int('Table', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Row(self):
        return self._get_int('Row')

    def put_Row(self, value):
        if self._set_int('Row', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Field(self):
        return self._get_int('Field')

    def put_Field(self, value):
        if self._set_int('Field', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FieldType(self):
        return self._get_int('FieldType')

    def put_FieldType(self, value):
        if self._set_int('FieldType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CommandBuffer(self):
        return self._get_buff('CommandBuffer')

    def put_CommandBuffer(self, value):
        if self._set_buff('CommandBuffer', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_AnswerBuffer(self):
        return self._get_buff('AnswerBuffer')

    def get_DateEnd(self):
        func = self.GET_TRIPLE_INT_PROTOTYPE((self._getter_name('DateEnd'), self.library))
        year = ctypes.c_int(0)
        month = ctypes.c_int(0)
        day = ctypes.c_int(0)
        func(self.interface, ctypes.pointer(day), ctypes.pointer(month), ctypes.pointer(year))
        return [day.value, month.value, year.value]

    def put_DateEnd(self, date):
        func = self.SET_TRIPLE_INT_PROTOTYPE((self._setter_name('DateEnd'), self.library))
        func(self.interface, ctypes.c_int(date[0]), ctypes.c_int(date[1]), ctypes.c_int(date[2]))
        return self.get_Result()

    def get_SessionEnd(self):
        return self._get_int('SessionEnd')

    def put_SessionEnd(self, value):
        if self._set_int('SessionEnd', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_EKLZFlags(self):
        return self._get_int('EKLZFlags')

    def get_EKLZKPKNumber(self):
        return self._get_int('EKLZKPKNumber')

    def put_EKLZKPKNumber(self, value):
        if self._set_int('EKLZKPKNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_UnitType(self):
        return self._get_int('UnitType')

    def put_UnitType(self, value):
        if self._set_int('UnitType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PictureNumber(self):
        return self._get_int('PictureNumber')

    def put_PictureNumber(self, value):
        if self._set_int('PictureNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_LeftMargin(self):
        return self._get_int('LeftMargin')

    def put_LeftMargin(self, value):
        if self._set_int('LeftMargin', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Memory(self):
        return self._get_int('Memory')

    def get_PictureState(self):
        return self._get_int('PictureState')

    def get_Width(self):
        return self._get_int('Width')

    def put_Width(self, value):
        if self._set_int('Width', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Operator(self):
        return self._get_int('Operator')

    def put_Operator(self, value):
        if self._set_int('Operator', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontBold(self):
        return self._get_bool('FontBold')

    def put_FontBold(self, value):
        if self._set_bool('FontBold', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontItalic(self):
        return self._get_bool('FontItalic')

    def put_FontItalic(self, value):
        if self._set_bool('FontItalic', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontNegative(self):
        return self._get_bool('FontNegative')

    def put_FontNegative(self, value):
        if self._set_bool('FontNegative', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontUnderline(self):
        return self._get_bool('FontUnderline')

    def put_FontUnderline(self, value):
        if self._set_bool('FontUnderline', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontDblHeight(self):
        return self._get_bool('FontDblHeight')

    def put_FontDblHeight(self, value):
        if self._set_bool('FontDblHeight', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FontDblWidth(self):
        return self._get_bool('FontDblWidth')

    def put_FontDblWidth(self, value):
        if self._set_bool('FontDblWidth', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PrintPurpose(self):
        return self._get_int('PrintPurpose')

    def put_PrintPurpose(self, value):
        if self._set_int('PrintPurpose', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReceiptFont(self):
        return self._get_int('ReceiptFont')

    def put_ReceiptFont(self, value):
        if self._set_int('ReceiptFont', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReceiptFontHeight(self):
        return self._get_int('ReceiptFontHeight')

    def put_ReceiptFontHeight(self, value):
        if self._set_int('ReceiptFontHeight', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReceiptBrightness(self):
        return self._get_int('ReceiptBrightness')

    def put_ReceiptBrightness(self, value):
        if self._set_int('ReceiptBrightness', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReceiptLinespacing(self):
        return self._get_int('ReceiptLinespacing')

    def put_ReceiptLinespacing(self, value):
        if self._set_int('ReceiptLinespacing', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_JournalFont(self):
        return self._get_int('JournalFont')

    def put_JournalFont(self, value):
        if self._set_int('JournalFont', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_JournalFontHeight(self):
        return self._get_int('JournalFontHeight')

    def put_JournalFontHeight(self, value):
        if self._set_int('JournalFontHeight', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_JournalBrightness(self):
        return self._get_int('JournalBrightness')

    def put_JournalBrightness(self, value):
        if self._set_int('JournalBrightness', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_JournalLinespacing(self):
        return self._get_int('JournalLinespacing')

    def put_JournalLinespacing(self, value):
        if self._set_int('JournalLinespacing', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_SummPointPosition(self):
        return self._get_int('SummPointPosition')

    def put_SummPointPosition(self, value):
        if self._set_int('SummPointPosition', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_QuantityPointPosition(self):
        return self._get_int('QuantityPointPosition')

    def put_QuantityPointPosition(self, value):
        if self._set_int('QuantityPointPosition', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Destination(self):
        return self._get_int('Destination')

    def put_Destination(self, value):
        if self._set_int('Destination', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TaxNumber(self):
        return self._get_int('TaxNumber')

    def put_TaxNumber(self, value):
        if self._set_int('TaxNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodePrintType(self):
        return self._get_int('BarcodePrintType')

    def put_BarcodePrintType(self, value):
        if self._set_int('BarcodePrintType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeControlCode(self):
        return self._get_bool('BarcodeControlCode')

    def put_BarcodeControlCode(self, value):
        if self._set_bool('BarcodeControlCode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeCorrection(self):
        return self._get_int('BarcodeCorrection')

    def put_BarcodeCorrection(self, value):
        if self._set_int('BarcodeCorrection', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeEncoding(self):
        return self._get_int('BarcodeEncoding')

    def put_BarcodeEncoding(self, value):
        if self._set_int('BarcodeEncoding', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeEncodingMode(self):
        return self._get_int('BarcodeEncodingMode')

    def put_BarcodeEncodingMode(self, value):
        if self._set_int('BarcodeEncodingMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FeedValue(self):
        return self._get_int('FeedValue')

    def put_FeedValue(self, value):
        if self._set_int('FeedValue', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ClsPtr(self):
        return self._get_void_ptr('ClsPtr')

    def get_PixelLineLength(self):
        return self._get_int('PixelLineLength')

    def get_RcpPixelLineLength(self):
        return self._get_int('RcpPixelLineLength')

    def get_JrnPixelLineLength(self):
        return self._get_int('JrnPixelLineLength')

    def get_SlipPixelLineLength(self):
        return self._get_int('SlipPixelLineLength')

    def get_RcpCharLineLength(self):
        return self._get_int('RcpCharLineLength')

    def get_JrnCharLineLength(self):
        return self._get_int('JrnCharLineLength')

    def get_SlipCharLineLength(self):
        return self._get_int('SlipCharLineLength')

    def get_Count(self):
        return self._get_int('Count')

    def put_Count(self, value):
        if self._set_int('Count', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_SlotNumber(self):
        return self._get_int('SlotNumber')

    def put_SlotNumber(self, value):
        if self._set_int('SlotNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DrawerOpened(self):
        return self._get_bool('DrawerOpened')

    def get_CoverOpened(self):
        return self._get_bool('CoverOpened')

    def get_BatteryLow(self):
        return self._get_bool('BatteryLow')

    def get_VerHi(self):
        return self._get_buff('VerHi')

    def get_VerLo(self):
        return self._get_buff('VerLo')

    def get_Build(self):
        return self._get_buff('Build')

    def get_Codepage(self):
        return self._get_int('Codepage')

    def get_LogicalNumber(self):
        return self._get_int('LogicalNumber')

    def put_LogicalNumber(self, value):
        if self._set_int('LogicalNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Remainder(self):
        return self._get_double('Remainder')

    def get_Change(self):
        return self._get_double('Change')

    def get_OperationType(self):
        return self._get_int('OperationType')

    def put_OperationType(self, value):
        if self._set_int('OperationType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DiscountNumber(self):
        return self._get_int('DiscountNumber')

    def put_DiscountNumber(self, value):
        if self._set_int('DiscountNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CounterType(self):
        return self._get_int('CounterType')

    def put_CounterType(self, value):
        if self._set_int('CounterType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PowerSupplyValue(self):
        return self._get_double('PowerSupplyValue')

    def get_PowerSupplyState(self):
        return self._get_int('PowerSupplyState')

    def get_StepCounterType(self):
        return self._get_int('StepCounterType')

    def put_StepCounterType(self, value):
        if self._set_int('StepCounterType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PowerSupplyType(self):
        return self._get_int('PowerSupplyType')

    def put_PowerSupplyType(self, value):
        if self._set_int('PowerSupplyType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodePixelProportions(self):
        return self._get_int('BarcodePixelProportions')

    def put_BarcodePixelProportions(self, value):
        if self._set_int('BarcodePixelProportions', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeProportions(self):
        return self._get_int('BarcodeProportions')

    def put_BarcodeProportions(self, value):
        if self._set_int('BarcodeProportions', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeColumns(self):
        return self._get_int('BarcodeColumns')

    def put_BarcodeColumns(self, value):
        if self._set_int('BarcodeColumns', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeRows(self):
        return self._get_int('BarcodeRows')

    def put_BarcodeRows(self, value):
        if self._set_int('BarcodeRows', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodePackingMode(self):
        return self._get_int('BarcodePackingMode')

    def put_BarcodePackingMode(self, value):
        if self._set_int('BarcodePackingMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeUseProportions(self):
        return self._get_bool('BarcodeUseProportions')

    def put_BarcodeUseProportions(self, value):
        if self._set_bool('BarcodeUseProportions', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeUseRows(self):
        return self._get_bool('BarcodeUseRows')

    def put_BarcodeUseRows(self, value):
        if self._set_bool('BarcodeUseRows', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeUseColumns(self):
        return self._get_bool('BarcodeUseColumns')

    def put_BarcodeUseColumns(self, value):
        if self._set_bool('BarcodeUseColumns', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeUseCorrection(self):
        return self._get_bool('BarcodeUseCorrection')

    def put_BarcodeUseCorrection(self, value):
        if self._set_bool('BarcodeUseCorrection', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeUseCodeWords(self):
        return self._get_bool('BarcodeUseCodeWords')

    def put_BarcodeUseCodeWords(self, value):
        if self._set_bool('BarcodeUseCodeWords', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeInvert(self):
        return self._get_bool('BarcodeInvert')

    def put_BarcodeInvert(self, value):
        if self._set_bool('BarcodeInvert', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeSave(self):
        return self._get_bool('BarcodeSave')

    def put_BarcodeSave(self, value):
        if self._set_bool('BarcodeSave', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeDeferredPrint(self):
        return self._get_bool('BarcodeDeferredPrint')

    def put_BarcodeDeferredPrint(self, value):
        if self._set_bool('BarcodeDeferredPrint', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeNumber(self):
        return self._get_int('BarcodeNumber')

    def put_BarcodeNumber(self, value):
        if self._set_int('BarcodeNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DrawerOnTimeout(self):
        return self._get_int('DrawerOnTimeout')

    def put_DrawerOnTimeout(self, value):
        if self._set_int('DrawerOnTimeout', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DrawerOffTimeout(self):
        return self._get_int('DrawerOffTimeout')

    def put_DrawerOffTimeout(self, value):
        if self._set_int('DrawerOffTimeout', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DrawerOnQuantity(self):
        return self._get_int('DrawerOnQuantity')

    def put_DrawerOnQuantity(self, value):
        if self._set_int('DrawerOnQuantity', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Frequency(self):
        return self._get_int('Frequency')

    def put_Frequency(self, value):
        if self._set_int('Frequency', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Duration(self):
        return self._get_int('Duration')

    def put_Duration(self, value):
        if self._set_int('Duration', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Directory(self):
        return self._get_buff('Directory')

    def put_Directory(self, value):
        if self._set_buff('Directory', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileSize(self):
        return self._get_int('FileSize')

    def put_FileSize(self, value):
        if self._set_int('FileSize', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileOpenType(self):
        return self._get_int('FileOpenType')

    def put_FileOpenType(self, value):
        if self._set_int('FileOpenType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileOpenMode(self):
        return self._get_int('FileOpenMode')

    def put_FileOpenMode(self, value):
        if self._set_int('FileOpenMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileOffset(self):
        return self._get_int('FileOffset')

    def put_FileOffset(self, value):
        if self._set_int('FileOffset', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FileReadSize(self):
        return self._get_int('FileReadSize')

    def put_FileReadSize(self, value):
        if self._set_int('FileReadSize', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_NeedResultFlag(self):
        return self._get_int('NeedResultFlag')

    def put_NeedResultFlag(self, value):
        if self._set_int('NeedResultFlag', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetMode(self):
        if self._exec_method('SetMode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ResetMode(self):
        if self._exec_method('ResetMode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Beep(self):
        if self._exec_method('Beep') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenDrawer(self):
        if self._exec_method('OpenDrawer') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def FullCut(self):
        if self._exec_method('FullCut') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PartialCut(self):
        if self._exec_method('PartialCut') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Feed(self):
        if self._exec_method('Feed') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetStatus(self):
        if self._exec_method('GetStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetRegister(self):
        if self._exec_method('GetRegister') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetRange(self):
        if self._exec_method('GetRange') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetSumm(self):
        if self._exec_method('GetSumm') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenSession(self):
        if self._exec_method('OpenSession') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CashIncome(self):
        if self._exec_method('CashIncome') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CashOutcome(self):
        if self._exec_method('CashOutcome') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Report(self):
        if self._exec_method('Report') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def NewDocument(self):
        if self._exec_method('NewDocument') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenCheck(self):
        if self._exec_method('OpenCheck') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Registration(self):
        if self._exec_method('Registration') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Annulate(self):
        if self._exec_method('Annulate') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Return(self):
        if self._exec_method('Return') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Buy(self):
        if self._exec_method('Buy') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BuyReturn(self):
        if self._exec_method('BuyReturn') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BuyAnnulate(self):
        if self._exec_method('BuyAnnulate') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Storno(self):
        if self._exec_method('Storno') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Discount(self):
        if self._exec_method('Discount') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Charge(self):
        if self._exec_method('Charge') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ResetChargeDiscount(self):
        if self._exec_method('ResetChargeDiscount') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Payment(self):
        if self._exec_method('Payment') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def StornoPayment(self):
        if self._exec_method('StornoPayment') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CancelCheck(self):
        if self._exec_method('CancelCheck') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CloseCheck(self):
        if self._exec_method('CloseCheck') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SummTax(self):
        if self._exec_method('SummTax') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def StornoTax(self):
        if self._exec_method('StornoTax') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintString(self):
        if self._exec_method('PrintString') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AddTextField(self):
        if self._exec_method('AddTextField') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintFormattedText(self):
        if self._exec_method('PrintFormattedText') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintHeader(self):
        if self._exec_method('PrintHeader') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintFooter(self):
        if self._exec_method('PrintFooter') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BeginDocument(self):
        if self._exec_method('BeginDocument') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EndDocument(self):
        if self._exec_method('EndDocument') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintBarcode(self):
        if self._exec_method('PrintBarcode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintPicture(self):
        if self._exec_method('PrintPicture') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetPictureArrayStatus(self):
        if self._exec_method('GetPictureArrayStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetPictureStatus(self):
        if self._exec_method('GetPictureStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintPictureByNumber(self):
        if self._exec_method('PrintPictureByNumber') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AddPicture(self):
        if self._exec_method('AddPicture') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AddPictureFromFile(self):
        if self._exec_method('AddPictureFromFile') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def DeleteLastPicture(self):
        if self._exec_method('DeleteLastPicture') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ClearPictureArray(self):
        if self._exec_method('ClearPictureArray') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetPicture(self):
        if self._exec_method('GetPicture') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintBarcodeByNumber(self):
        if self._exec_method('PrintBarcodeByNumber') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ClearBarcodeArray(self):
        if self._exec_method('ClearBarcodeArray') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def DeleteLastBarcode(self):
        if self._exec_method('DeleteLastBarcode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetBarcode(self):
        if self._exec_method('GetBarcode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BeginReport(self):
        if self._exec_method('BeginReport') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetRecord(self):
        if self._exec_method('GetRecord') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EndReport(self):
        if self._exec_method('EndReport') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BeginAdd(self):
        if self._exec_method('BeginAdd') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetRecord(self):
        if self._exec_method('SetRecord') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EndAdd(self):
        if self._exec_method('EndAdd') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetCaption(self):
        if self._exec_method('SetCaption') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetCaption(self):
        if self._exec_method('GetCaption') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetValue(self):
        if self._exec_method('SetValue') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetValue(self):
        if self._exec_method('GetValue') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetTableField(self):
        if self._exec_method('SetTableField') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetTableField(self):
        if self._exec_method('GetTableField') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Fiscalization(self):
        if self._exec_method('Fiscalization') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ResetSummary(self):
        if self._exec_method('ResetSummary') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetDate(self):
        if self._exec_method('SetDate') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetTime(self):
        if self._exec_method('SetTime') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetLicense(self):
        if self._exec_method('GetLicense') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetLicense(self):
        if self._exec_method('SetLicense') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def SetSerialNumber(self):
        if self._exec_method('SetSerialNumber') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def InitTables(self):
        if self._exec_method('InitTables') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def TechZero(self):
        if self._exec_method('TechZero') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def RunCommand(self):
        if self._exec_method('RunCommand') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def FlushBuffer(self):
        if self._exec_method('FlushBuffer') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ClearOutput(self):
        if self._exec_method('ClearOutput') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EKLZActivate(self):
        if self._exec_method('EKLZActivate') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EKLZCloseArchive(self):
        if self._exec_method('EKLZCloseArchive') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EKLZGetStatus(self):
        if self._exec_method('EKLZGetStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def WriteData(self):
        if self._exec_method('WriteData') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOff(self):
        if self._exec_method('PowerOff') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def DemoPrint(self):
        if self._exec_method('DemoPrint') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def TestConnector(self):
        if self._exec_method('TestConnector') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Sound(self):
        if self._exec_method('Sound') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AdvancedOpenDrawer(self):
        if self._exec_method('AdvancedOpenDrawer') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenDirectory(self):
        if self._exec_method('OpenDirectory') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadDirectory(self):
        if self._exec_method('ReadDirectory') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CloseDirectory(self):
        if self._exec_method('CloseDirectory') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenFile(self):
        if self._exec_method('OpenFile') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CloseFile(self):
        if self._exec_method('CloseFile') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def DeleteFileFromSD(self):
        if self._exec_method('DeleteFileFromSD') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def WriteFileToSD(self):
        if self._exec_method('WriteFileToSD') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadFile(self):
        if self._exec_method('ReadFile_') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PrintLastCheckCopy(self):
        if self._exec_method('PrintLastCheckCopy') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def _doCallback(self, data, size):
        if self.callback is not None:
            return self.callback(self, data, size)
        return 0

    SCANNER_EVENT_HANDLER_FUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int)

    def InitScannerEventHandler(self):
        self._callback = self.SCANNER_EVENT_HANDLER_FUNC(self._doCallback)
        self.library.put_ScannerEventHandlerFunc(self.interface, self._callback)

    def get_ScannerPortHandler(self):
        return self._get_void_ptr('ScannerPortHandler')

    def put_ScannerEventHandler(self, handler):
        if self._set_void_ptr('ScannerEventHandler', handler) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ScannerMode(self):
        return self._get_int('ScannerMode')

    def put_ScannerMode(self, value):
        if self._set_int('ScannerMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def WritePinPad(self):
        if self._exec_method('WritePinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadPinPad(self):
        if self._exec_method('ReadPinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def WriteModem(self):
        if self._exec_method('WriteModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadModem(self):
        if self._exec_method('ReadModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenPinPad(self):
        if self._exec_method('OpenPinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ClosePinPad(self):
        if self._exec_method('ClosePinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def OpenModem(self):
        if self._exec_method('OpenModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CloseModem(self):
        if self._exec_method('CloseModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetModemStatus(self):
        if self._exec_method('GetModemStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetPinPadStatus(self):
        if self._exec_method('GetPinPadStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PinPadDevice(self):
        return self._get_void_ptr('PinPadDevice')

    def get_PinPadMode(self):
        return self._get_int('PinPadMode')

    def put_PinPadMode(self, value):
        if self._set_int('PinPadMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOnPinPad(self):
        if self._exec_method('PowerOnPinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOffPinPad(self):
        if self._exec_method('PowerOffPinPad') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemDevice(self):
        return self._get_void_ptr('ModemDevice')

    def get_ModemMode(self):
        return self._get_int('ModemMode')

    def put_ModemMode(self, value):
        if self._set_int('ModemMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOnModem(self):
        if self._exec_method('PowerOnModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOffModem(self):
        if self._exec_method('PowerOffModem') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ReadSize(self):
        return self._get_int('ReadSize')

    def put_ReadSize(self, value):
        if self._set_int('ReadSize', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemConnectionType(self):
        return self._get_int('ModemConnectionType')

    def put_ModemConnectionType(self, value):
        if self._set_int('ModemConnectionType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemPort(self):
        return self._get_int('ModemPort')

    def put_ModemPort(self, value):
        if self._set_int('ModemPort', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WriteSize(self):
        return self._get_int('WriteSize')

    def get_ModemStatus(self):
        return self._get_int('ModemStatus')

    def put_ModemStatus(self, value):
        if self._set_int('ModemStatus', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemSignal(self):
        return self._get_int('ModemSignal')

    def put_ModemSignal(self, value):
        if self._set_int('ModemSignal', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_OutOfPaper(self):
        return self._get_bool('OutOfPaper')

    def get_PrinterConnectionFailed(self):
        return self._get_bool('PrinterConnectionFailed')

    def get_PrinterMechanismError(self):
        return self._get_bool('PrinterMechanismError')

    def get_PrinterCutMechanismError(self):
        return self._get_bool('PrinterCutMechanismError')

    def get_PrinterOverheatError(self):
        return self._get_bool('PrinterOverheatError')

    def GetDeviceMetrics(self):
        if self._exec_method('GetDeviceMetrics') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetCurrentMode(self):
        if self._exec_method('GetCurrentMode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetCurrentStatus(self):
        if self._exec_method('GetCurrentStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetLastSummary(self):
        if self._exec_method('GetLastSummary') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemAddress(self):
        return self._get_buff('ModemAddress')

    def put_ModemAddress(self, value):
        if self._set_buff('ModemAddress', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_ModemOperator(self):
        return self._get_buff('ModemOperator')

    def get_ModemError(self):
        return self._get_buff('ModemError')

    def get_AdvancedMode(self):
        return self._get_int('AdvancedMode')

    def get_BottomMargin(self):
        return self._get_bool('BottomMargin')

    def put_BottomMargin(self, value):
        if self._set_bool('BottomMargin', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DeviceDescription(self):
        return self._get_buff('DeviceDescription')

    def get_EKLZKPK(self):
        return self._get_int('EKLZKPK')

    def EKLZGetKPK(self):
        if self._exec_method('EKLZGetKPK') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_BarcodeVersion(self):
        return self._get_int('BarcodeVersion')

    def put_BarcodeVersion(self, value):
        if self._set_int('BarcodeVersion', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TaxPassword(self):
        return self._get_buff('TaxPassword')

    def put_TaxPassword(self, value):
        if self._set_buff('TaxPassword', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def put_Classifier(self, value):
        if self._set_buff('Classifier', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_Classifier(self):
        return self._get_buff('Classifier')

    def put_FiscalPropertyNumber(self, value):
        if self._set_int('FiscalPropertyNumber', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FiscalPropertyNumber(self):
        return self._get_int('FiscalPropertyNumber')

    def put_FiscalPropertyType(self, value):
        if self._set_int('FiscalPropertyType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FiscalPropertyType(self):
        return self._get_int('FiscalPropertyType')

    def put_FiscalPropertyValue(self, value):
        if self._set_buff('FiscalPropertyValue', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FiscalPropertyValue(self):
        return self._get_buff('FiscalPropertyValue')

    def put_FiscalPropertyPrint(self, value):
        if self._set_bool('FiscalPropertyPrint', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FiscalPropertyPrint(self):
        return self._get_bool('FiscalPropertyPrint')

    def WriteFiscalProperty(self):
        if self._exec_method('WriteFiscalProperty') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadFiscalProperty(self):
        if self._exec_method('ReadFiscalProperty') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_HasNotSendedDocs(self):
        return self._get_bool('HasNotSendedDocs')

    def RunFNCommand(self):
        if self._exec_method('RunFNCommand') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_CounterDimension(self):
        return self._get_int('CounterDimension')

    def put_CounterDimension(self, value):
        if self._set_int('CounterDimension', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_DiscountInSession(self):
        return self._get_double('DiscountInSession')

    def get_ChargeInSession(self):
        return self._get_double('ChargeInSession')

    def get_NetworkError(self):
        return self._get_int('NetworkError')

    def get_OFDError(self):
        return self._get_int('OFDError')

    def get_FNError(self):
        return self._get_int('FNError')

    def get_TimeoutACK(self):
        return self._get_int('TimeoutACK')

    def put_TimeoutACK(self, value):
        if self._set_int('TimeoutACK', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TimeoutENQ(self):
        return self._get_int('TimeoutENQ')

    def put_TimeoutENQ(self, value):
        if self._set_int('TimeoutENQ', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AddBarcode(self):
        if self._exec_method('AddBarcode') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def GetBarcodeArrayStatus(self):
        if self._exec_method('GetBarcodeArrayStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def Correction(self):
        if self._exec_method('Correction') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReturnCorrection(self):
        if self._exec_method('ReturnCorrection') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BuyCorrection(self):
        if self._exec_method('BuyCorrection') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def BuyReturnCorrection(self):
        if self._exec_method('BuyReturnCorrection') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PrintCheck(self):
        return self._get_bool('PrintCheck')

    def put_PrintCheck(self, value):
        if self._set_bool('PrintCheck', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FNState(self):
        return self._get_int('FNState')

    def GetUnitVersion(self):
        if self._exec_method('GetUnitVersion') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TaxSum(self):
        return self._get_double('TaxSum')

    def put_TaxSum(self, value):
        if self._set_double('TaxSum', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_TaxMode(self):
        return self._get_int('TaxMode')

    def put_TaxMode(self, value):
        if self._set_int('TaxMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PositionType(self):
        return self._get_int('PositionType')

    def put_PositionType(self, value):
        if self._set_int('PositionType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_PositionPaymentType(self):
        return self._get_int('PositionPaymentType')

    def put_PositionPaymentType(self, value):
        if self._set_int('PositionPaymentType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def AddFiscalProperty(self):
        if self._exec_method('AddFiscalProperty') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ResetFiscalProperties(self):
        if self._exec_method('ResetFiscalProperties') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FfdVersion(self):
        return self._get_int('FfdVersion')

    def get_DeviceFfdVersion(self):
        return self._get_int('DeviceFfdVersion')

    def get_FNFfdVersion(self):
        return self._get_int('FNFfdVersion')

    def get_CommandCode(self):
        return self._get_int('CommandCode')

    def get_ErrorCode(self):
        return self._get_int('ErrorCode')

    def get_ErrorData(self):
        return self._get_buff('ErrorData')

    def get_PositionSum(self):
        return self._get_double('PositionSum')

    def put_PositionSum(self, value):
        if self._set_double('PositionSum', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def put_FiscalPropertyUser(self, value):
        if self._set_bool('FiscalPropertyUser', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FiscalPropertyUser(self):
        return self._get_bool('FiscalPropertyUser')

    def put_WiFiMode(self, value):
        if self._set_int('WiFiMode', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiMode(self):
        return self._get_int('WiFiMode')

    def WriteWiFi(self):
        if self._exec_method('WriteWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def ReadWiFi(self):
        if self._exec_method('ReadWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiDevice(self):
        return self._get_void_ptr('WiFiDevice')

    def PowerOnWiFi(self):
        if self._exec_method('PowerOnWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def PowerOffWiFi(self):
        if self._exec_method('PowerOffWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def put_WiFiConnectionType(self, value):
        if self._set_int('WiFiConnectionType', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiConnectionType(self):
        return self._get_int('WiFiConnectionType')

    def put_WiFiAddress(self, value):
        if self._set_int('WiFiAddress', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiAddress(self):
        return self._get_buff('WiFiAddress')

    def put_WiFiPort(self, value):
        if self._set_int('WiFiPort', value) is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiPort(self):
        return self._get_int('WiFiPort')

    def GetWiFiStatus(self):
        if self._exec_method('GetWiFiStatus') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_WiFiStatus(self):
        return self._get_int('WiFiStatus')

    def OpenWiFi(self):
        if self._exec_method('OpenWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def CloseWiFi(self):
        if self._exec_method('CloseWiFi') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def get_FNFiscal(self):
        return self._get_bool('FNFiscal')

    def get_ENVDMode(self):
        return self._get_bool('ENVDMode')

    def BeginFormFiscalProperty(self):
        if self._exec_method('BeginFormFiscalProperty') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()

    def EndFormFiscalProperty(self):
        if self._exec_method('EndFormFiscalProperty') is None:
            self._print_result(inspect.currentframe().f_code.co_name)
        return self.get_Result()
