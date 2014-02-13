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
import inspect
import time
from ConfigParser import RawConfigParser

# PATH OF WATCHED DIRECTORY
CONFIGURATION_DIRECTORY = os.path.expanduser('~/etc/')
# GLOBAL CONFIGURATION FILE
CONFIGURATION_FILE = 'configuration.conf'

import pyinotify

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE  # watched events
wdd = wm.add_watch(CONFIGURATION_DIRECTORY, mask, rec=True)

# KEYS FOR CONFIGURATION FILE

# DEFAULT SECTION
DEFAULT = 'DEFAULT'  # GLOBAL SECTION
MANUAL_RECONFIGURATION = 'manual_reconfiguration'  # KEY FOR DEFINING MANUAL_RECONFIGURATION.
LAST_RECONFIGURATION = 'last_reconfiguration'  # DATE OF LAST DEFAULT/LOCAL RECONFIGURATION.
RECONFIGURE = 'reconfigure'  # FLAGS USED TO DO A DEFAULT/LOCAL RECONFIGURATION.

# SPECIFIC TO SECTIONS
FILE = 'file'  # CONFIGURATION FILES PATH
LISTENER = 'listener'  # LISTENERS OF CONFIGURATION FILES. THE ORDER CORRESPONDS TO CONFIGURATION FILES ORDER

import clogging
_logger = clogging.getLogger()


class EventHandler(pyinotify.ProcessEvent):
    """
    File system handler which listen modification of configuration directory
    content and notifies configuration file bound observers.
    """

    def __init__(self):

        super(EventHandler, self).__init__()

        self.manual_reconfiguration = True
        self.configurationObservers = dict()
        self.config_parser = RawConfigParser()

        # register self among observers
        self.register_observer(
            CONFIGURATION_FILE, self._check_configuration, True)

    def _check_configuration(self, src_path):
        """
        Observer method.
        """

        _logger.debug('src_path: {0}'.format(src_path))

        self.config_parser.read(src_path)

        manual_reconfiguration = \
            self.config_parser.getboolean(DEFAULT, MANUAL_RECONFIGURATION)

        self.manual_reconfiguration = manual_reconfiguration

        files_to_reconfigure = list()

        for section in self.config_parser.sections():
            try:
                listener = self.config_parser.get(section, LISTENER)
                _file = self.config_parser.get(section, FILE)
                _reconfigure = self.config_parser.has_option(section, RECONFIGURE)
                function_listener = resolve_object(listener)
                if inspect.isfunction(function_listener):
                    self.register_observer(_file, function_listener, _reconfigure)
                if _reconfigure:
                    last_reconfiguration = time.ctime()
                    self.config_parser.set(section, LAST_RECONFIGURATION, last_reconfiguration)
                else:
                    files_to_reconfigure.append(_file)
            except Exception as e:
                _logger.error(e)

        reconfigure = self.config_parser.has_option(DEFAULT, RECONFIGURE)

        if reconfigure:
            if len(files_to_reconfigure) != 0:
                for file_to_reconfigure in files_to_reconfigure:
                    self.callObserver(file_to_reconfigure, True)
            else:
                self.callObservers()
            self.config_parser.remove_option(DEFAULT, RECONFIGURE)
            last_reconfiguration = time.ctime()
            self.config_parser.set(DEFAULT, LAST_RECONFIGURATION, last_reconfiguration)

        # save config_parser
        with open(src_path, 'w') as fp:
            self.config_parser.write(fp)

    def callObservers(self, call=False):
        """
        Call all observers.
        """

        _logger.debug('')

        for configuration_file, observer in \
                self.configurationObservers.iteritems():
            src_path = os.path.join(
                CONFIGURATION_DIRECTORY, configuration_file)
            self.callObserver(src_path, call)

    def register_observer(self, configuration_file, observer, call=False):
        """
        Register an observer bound to input configuration_file.
        If call is True, the observer is called just after registering.
        """

        _logger.debug(
            'configuration_file: {0}, observer: {1}, call: {2}'
            .format(configuration_file, observer, call))

        self.configurationObservers[configuration_file] = observer

        if call:
            src_path = os.path.join(
                CONFIGURATION_DIRECTORY, configuration_file)
            self.callObserver(src_path, call)

    def callObserver(self, src_path, call=False):
        """
        Call observer bound to event src_path.
        """

        _logger.debug('src_path: {0}'.format(src_path))

        src_path = os.path.expanduser(src_path)

        if call or not self.manual_reconfiguration:
            filename = os.path.basename(src_path)
            observer = self.configurationObservers.get(filename, None)

            if observer is not None:
                observer(src_path)

    def process_default(self, event):
        """
        Call when a configuration file is modified.
        """

        _logger.debug('event: {0}'.format(event))

        self.callObserver(event.pathname)

# singleton for configuration file system event handler
_event_handler = EventHandler()

_notifier = None


def schedule_observer():
    _notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
    _notifier.start()

#import threading
#t = threading.Thread(target=schedule_observer)
#t.start()

schedule_observer()

import atexit


@atexit.register
def _stop_observer():
    """
    Stop listening of configuration file event handler on configuration directory.
    """

    if _logger is not None:
        _logger.debug('')

    if _notifier is not None:
        _notifier.stop()
        _notifier.join()


def register_observer(configuration_file, observer, call=False):
    """
    Shortcut method which register an observer and bound it with input configuration_file.
    If call is True (False by default), the observer is called just after being registered.
    """

    _logger.debug(
        'configuration_file: {0}, observer: {1}, call: {2}'
        .format(configuration_file, observer, call))

    _event_handler.register_observer(
        configuration_file, observer, call)


def manual_reconfiguration(manual_reconfiguration=None):
    """
    Returns configuration file handler manual reconfiguration status.
    If input manual_reconfiguration is given, change the status.
    """

    _logger.debug(
        'manual_reconfiguration: {0}'
        .format(manual_reconfiguration))

    if manual_reconfiguration is not None:
        _event_handler.manual_reconfiguration = \
            manual_reconfiguration

    return _event_handler.manual_reconfiguration

if __name__ == '__main__':
    """
    Script execution.
    """

    import sys

    if len(sys.argv) > 1:
        for conf_file in sys.argv[1:]:
            src_path = os.path.join(CONFIGURATION_DIRECTORY, conf_file)
            _event_handler.callObserver(src_path, True)
    else:
        _event_handler.callObservers(True)


def resolve_object(namespace):
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
