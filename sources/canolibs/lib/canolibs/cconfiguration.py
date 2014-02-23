#!/usr/bin/env python
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

import os.path
import time
from ConfigParser import RawConfigParser

# PATH OF WATCHED DIRECTORY
CONFIGURATION_DIRECTORY = os.path.expanduser('~/etc/')
# GLOBAL CONFIGURATION FILE
CONFIGURATION_FILE = 'configuration.conf'

# KEYS FOR CONFIGURATION FILE
# DEFAULT SECTION
DEFAULT = 'DEFAULT'  # GLOBAL SECTION
RECONFIGURATION = 'reconfiguration'  # KEY FOR MANUAL/AUTO/ONCE RECONFIGURATION.
MANUAL = 0  # manual reconfiguration
AUTO = 1  # auto reconfiguration
ONCE = 2  # do a reconfiguration
ONCE_MANUAL = ONCE | MANUAL  # ONCE then MANUAL mode
ONCE_AUTO = ONCE | AUTO  # ONCE then AUTO mode
LAST_RECONFIGURATION = 'last_reconfiguration'  # DATE OF LAST DEFAULT/LOCAL RECONFIGURATION.

# SPECIFIC TO SECTIONS
PATH = 'path'  # CONFIGURATION FILE PATH
WATCHER = 'watcher'  # CONFIGURATION FILE WATCHER.
NOTIFIER = 'notifier'  # NOTIFIER

import logging
logger = logging.getLogger()

from pyinotify import WatchManager, ThreadedNotifier, ProcessEvent, IN_MODIFY, IN_CREATE


class ConfigurationManager(object):

    def __init__(
        self,
        path=CONFIGURATION_DIRECTORY,
        file_name=CONFIGURATION_FILE,
        reconfiguration=MANUAL
    ):
        self.path = path
        self.file_name = file_name
        self.reconfiguration = reconfiguration
        self.watchers = dict()

        self.in_watching = False
        self.config_parser = RawConfigParser()

        self.register_watcher(DEFAULT, self.watch, self.file_name, self.reconfiguration)

    def get_file_path(self, file_name):

        result = os.path.join(self.path, file_name)
        return result

    def unregister_watcher(self, name):

        watcher = self.watchers.get(name)
        if watcher is not None:
            watcher.stop()
            del self.watchers[name]

    def register_watcher(
        self, name, watch, file_name, reconfiguration=MANUAL
    ):
        self.unregister_watcher(name)
        watcher = Watcher(name, self, watch, file_name, reconfiguration)
        self.watchers[name] = watcher

    def watch(self, conf_path):

        if self.in_watching:
            return
        self.in_watching = True

        self.config_parser.read(conf_path)

        self.reconfiguration = \
            self.config_parser.getint(DEFAULT, RECONFIGURATION)

        for section in self.config_parser.sections():
            try:
                path = self.config_parser.get(section, PATH)
                reconfiguration = self.config_parser.getint(
                    section, RECONFIGURATION)
                watcher = self.config_parser.get(section, WATCHER)
                watch = ConfigurationManager.resolve_watcher(watcher)
                self.register_watcher(
                    section, watch, path, reconfiguration)

                if self.reconfiguration & ONCE or watcher.reconfiguration & ONCE:
                    # delete ONCE flag
                    watcher.reconfiguration &= AUTO
                    # update reconfiguration and last_reconfiguration fields
                    self.config_parser.set(
                        section, RECONFIGURATION, watcher.reconfiguration)
                    self.config_parser.set(
                        section, LAST_RECONFIGURATION, time.ctime())

            except Exception as e:
                logger.error(e)

        if self.reconfiguration & ONCE:
            # delete ONCE flag
            self.reconfiguration &= AUTO

            self.config_parser.set(DEFAULT, RECONFIGURATION, self.reconfiguration)
            self.config_parser.set(DEFAULT, LAST_RECONFIGURATION, time.ctime())

        with open(conf_path, 'w+') as conf_file:
            self.config_parser.write(conf_file)

        self.in_watching = False

    def call_watcher(self, name):

        watcher = self.watchers.get(name)
        file_path = self.get_file_path(watcher.file_name)
        if watcher is not None:
            watcher.watch(file_path)

    def stop(self):
        for watcher in self.watchers.itervalues():
            watcher.stop()

    def start(self):
        for watcher in self.watchers.itervalues():
            watcher.start()

    def _update(self, name):

        file_path = self.get_file_path(self.file_name)
        self.config_parser.read(file_path)
        self.config_parser.set_option(name, LAST_RECONFIGURATION, time.ctime())

        with open(file_path, 'w+') as conf_file:
            self.config_parser.write(conf_file)

    @staticmethod
    def resolve_watcher(namespace):
        """
        Try to get an object reference from a namespace.
        Raise an ImportError if namespace is not known from this environment.
        """

        result = None
        _globals = globals()

        if namespace not in _globals:
            splitted_namespace = namespace.split('.')
            result = __import__(splitted_namespace[0])
            for intermediate_namespace in splitted_namespace[1:]:
                try:
                    result = getattr(result, intermediate_namespace)
                except AttributeError as AE:
                    raise ImportError(AE)

        return result


class Watcher(ProcessEvent):

    MASK = IN_MODIFY | IN_CREATE

    def __init__(
        self,
        name,
        configuration_manager,
        watch,
        file_name,
        reconfiguration=MANUAL
    ):
        self.name = name
        self.configuration_manager = configuration_manager
        self.watch = watch
        self.file_name = file_name
        self.reconfiguration = reconfiguration

        self.watch_manager = WatchManager()
        self.notifier = ThreadedNotifier(self.watch_manager, self)

        file_path = configuration_manager.get_file_path(file_name)
        self.watch_manager.add_watch(file_path, Watcher.MASK)

        if reconfiguration & ONCE:
            self.watch(file_path)

    def process_DEFAULT(self, event):

        if self.reconfiguration:
            self.watch(event.path)

            self.configuration_manager._update(self.name)

    def process_IN_MODIFY(self, event):
        self.process_DEFAULT(event)

    def process_IN_CREATE(self, event):
        self.process_DEFAULT(event)

    def start(self):
        self.notifier.start()

    def stop(self):
        if self.notifier.is_alive():
            self.notifier.stop()
