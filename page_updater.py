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
        for repo in self.paths_to_repositories:
            access = None

            try:
                print ('Проверка доступа к {}'.format(repo))

                self.changeValueById('message', u"Проверка доступа к {}".format(repo))
                subprocess.check_output('cd {}/{}; git fetch'.format(self.home_dir, repo),
                                        shell=True,
                                        stderr=subprocess.STDOUT)
                logging.getLogger(__name__).info(u"Доступ к {} получен".format(repo))
                access=True

            except subprocess.CalledProcessError:
                logging.getLogger(__name__).error(u"Ошибка доступа к {}".format(repo))
                print ('Ошибка доступа к {}'.format(repo))
                access=False
        
            if access == False:
                break 

        if access == True:
            self.check_local_changes()

        else:
            self.changeValueById('message', u"Обновление ПО невозможно. Нет доступа.")
            self.setElementEnabled("back", True)
    

    def check_local_changes(self):
        CHANGES_NOT_STAGED_FOR_COMMIT = "Changes not staged for commit"
        CONTENT_MODIFIED = "Content modified"
        NEW_COMMITS = "New commits"

        logging.getLogger(__name__).info(u'Проверка локальных изменений в репозиториях')

        for repo in self.paths_to_repositories:

            self.changeValueById('message', u"Проверка локальных изменений в {}".format(repo))
            output = subprocess.check_output('cd {}/{}; git status'.format(self.home_dir, repo),
                                             shell=True, stderr=subprocess.STDOUT)

            if output == CHANGES_NOT_STAGED_FOR_COMMIT:
                print('Имеются локальные изменения в {}'.format(repo))
                logging.getLogger(__name__).check_output(u'Имеются локальные изменения в {}'.format(repo))
            
            elif output == CONTENT_MODIFIED:
                print('Обновление невозможно в {}'.format(repo))
                logging.getLogger(__name__).error(u'Обновление невозможно в {}'.format(repo))

            elif output == NEW_COMMITS:
                print('Есть новые комиты обновлятся можно в {}'.format(repo))
                logging.getLogger(__name__).info(u'Есть новые коммиты обновляться можно в {}'.format(repo))
        
            else:
                print('Обновление невозможно, git status вернул иное. '.format(repo))
                logging.getLogger(__name__).error(u'обновление невозможно в {}'.format(repo))

        if output == CONTENT_MODIFIED:
            self.changeValueById('message', u"Обновление ПО невозможно. Имеются локальные изменения.")

        else:
            self.changeValueById('message', u"Обновление ПО возможно")
            self.setElementEnabled("update", True)

        self.setElementEnabled("back", True)

