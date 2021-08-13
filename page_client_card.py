# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import config

class PageClientCard(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "balance":
            self.operationScenario.setPayDescription(u'Баланс клиентской карты')
            self.operationScenario.setCardClosePurpose(OperationScenario.CARD_CLOSE_PURPOSE_SHOW_BALANCE)
            self.switchTo("PageCardClose", card_type=u"клиентскую")
        elif button == "fill":
            self.operationScenario.setPayDescription(u'Пополнение клиентской карты')
            self.operationScenario.setWaitFixedSum(False)
            self.operationScenario.setPayDestination(OperationScenario.PAY_DEST_CLIENT_CARD_FILL)
            self.operationScenario.setCardClosePurpose(OperationScenario.CARD_CLOSE_PURPOSE_FILL_CARD)
            self.switchTo("PageCardClose", card_type=u"клиентскую")
        elif button == "buy":
            self.operationScenario.setPayDescription(u'Покупка клиентской карты')
            self.operationScenario.setWaitFixedSum(True)
            self.operationScenario.setPayDestination(OperationScenario.PAY_DEST_CLIENT_CARD_BUY)
            self.operationScenario.setCardClosePurpose(OperationScenario.CARD_CLOSE_PURPOSE_BUY_CARD)
            self.operationScenario.setSpendingSum(self.operationScenario.getCardPrice())
            self.switchTo("PageSelPay", pay_description = self.operationScenario.generateDescription())
        elif button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.cardDispenserCheckStatus()
        if self.operationScenario.getCardDispenserStackEmpty() or self.operationScenario.isCardDispenserFailed():
            self.setElementEnabled("buy", False)

        if config.getProperty("debug_emualete_card_dispenser", default=False, _type='bool'):
            self.setElementEnabled("buy", True)

        if not self.operationScenario.atolModeOnlyQrCodeCheck():
            self.operationScenario.setHasPaper(self.operationScenario.checkHasPaper())

    def onExit(self, nextPage, *args, **kwargs):
        pass
        # logging.info(__name__ + " Exit page")
