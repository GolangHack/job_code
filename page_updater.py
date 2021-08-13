# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import os
import subprocess
from pyutils.delay import Delay


class PageUpdater(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "back":
            self.switchTo("PageAdministartorMenu")
        if button == "check_possibility_updating":
            self.changeValueById('message', u"Подождите, идет проверка возможности обновления.")
            self.setElementEnabled("check_possibility_updating", False)
            self.setElementEnabled("back", False)
            Delay.once(1, self.check_connection_with_repos)
        if button == "update":
            try:
                os.system("cd {}/updater && ./start_update.sh".format(self.home_dir))
            except IOError:
                logging.getLogger(__name__).error(u"Ошибка запуска обновления. Не найден start_update.sh")
                self.changeValueById('message', u"Ошибка запуска обновления.")
                self.setElementEnabled("update", False)

    def preEnter(self, previousPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.home_dir = os.path.expanduser("~")
        try:
            with open("{}/updater/currently_version".format(self.home_dir)) as currently_version_file:
                currently_version = currently_version_file.read()
            with open("{}/updater/actual_version".format(self.home_dir)) as actual_version_file:
                actual_version = actual_version_file.read()
            self.setVariable(
                versions=u"Текущая версия ПО: {}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀Актуальная версия ПО: {}".format(
                    currently_version, actual_version))
            if currently_version == actual_version:
                self.setElementEnabled("check_possibility_updating", False)
            self.setElementEnabled("update", False)
            self.changeValueById('message', u"Проверьте возможность обновления, а затем обновите ПО.")
        except IOError:
            self.changeValueById('message', u"Ошибка. Нет данных о текущей и актуальной версии.")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.paths_to_repositories = ['python', 'python/atol', 'python/bankacquiring',
                                      'python/billkeeper', 'python/carddispenser',
                                      'python/data_storage', 'python/htmlpy_core', 'python/rplclib',
                                      'python/billkeeper/esspapi', 'bin/datareplicatorslave']
        if os.path.exists("{}/bin/queueviewer".format(self.home_dir)):
            self.paths_to_repositories.append("bin/queueviewer")
        if os.path.exists("{}/python/themes/robotcarwashorange".format(self.home_dir)):
            self.paths_to_repositories.append("python/themes/robotcarwashorange")
        if os.path.exists("{}/python/themes/aquabotblueyellow".format(self.home_dir)):
            self.paths_to_repositories.append("python/themes/aquabotblueyellow")

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")

    def check_connection_with_repos(self):
        access_list = []
        for repo in self.paths_to_repositories:
            try:
                print 'Проверка доступа к {}'.format(repo)
                self.changeValueById('message', u"Проверка доступа к {}".format(repo))
                subprocess.check_output('cd {}/{}; git fetch'.format(self.home_dir, repo),
                                        shell=True,
                                        stderr=subprocess.STDOUT)
                logging.getLogger(__name__).info(u"Доступ к {} получен".format(repo))
                access_list.append('1')
            except subprocess.CalledProcessError:
                logging.getLogger(__name__).error(u"Ошибка доступа к {}".format(repo))
                print 'Ошибка доступа к {}'.format(repo)
                access_list.append('0')
        if '0' not in access_list:
            self.check_local_changes()
        else:
            self.changeValueById('message', u"Обновление ПО невозможно. Нет доступа.")
            self.setElementEnabled("back", True)

    def check_local_changes(self):
        repos_with_local_changes = []
        logging.getLogger(__name__).info(u'Проверка локальных изменений в репозиториях')
        for repo in self.paths_to_repositories:
            self.changeValueById('message', u"Проверка локальных изменений в {}".format(repo))
            output = subprocess.check_output('cd {}/{}; git status'.format(self.home_dir, repo),
                                             shell=True, stderr=subprocess.STDOUT)
            if 'Changes not staged for commit' in output:
                repos_with_local_changes.append('1')
                print('Имеются локальные изменения в {}'.format(repo))
                logging.getLogger(__name__).error(u'Имеются локальные изменения в {}'.format(repo))
            else:
                repos_with_local_changes.append('0')
                print('Нет локальных изменений в {}'.format(repo))
                logging.getLogger(__name__).info(u'Нет локальных изменений в {}'.format(repo))
        if '1' in repos_with_local_changes:
            self.changeValueById('message', u"Обновление ПО невозможно. Имеются локальные изменения.")
        else:
            self.changeValueById('message', u"Обновление ПО возможно")
            self.setElementEnabled("update", True)
        self.setElementEnabled("back", True)
