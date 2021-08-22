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