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

"""
Loads dynamically referentials which are accessible through the referentials field.
A referential must provide such methods:
- get_entities(*rks): get all referential entities related to input rk. All if rk is empty.
- get_topologies(*rks): get all referential topologies related to input rks. All if rks is empty.
- send_entities(*entities): send entities related to rk. All if entities is empty.
- get_foreign_key(*document): get foreign key field, or value if document is not None.
"""

import ConfigParser
import pymongo

REFERENTIAL_CONFIGURATION_PATH = 'referentials.conf'
LIBRARY = 'library'
BINDING = 'binding'

referentials = dict()


def update_configuration(src_path):
    """
    Update a configuration related to input src_path
    """

    config_parser = ConfigParser.RawConfigParser()

    config_parser.read(src_path)

    for section in config_parser.sections():
        referential = referentials.get(section)
        if referential is None:
            referential = dict()
            referentials[section] = referential

            library = config_parser.get(section, LIBRARY)
            referential[LIBRARY] = import_library(library)
            referential[BINDING] = config_parser.get(section, BINDING)


def get_foreign_keys(*documents):
    """
    Get documents foreign key. None if it does not exist.
    If documents is Empty, returns itop foreign key.
    """

    result = dict()

    for name, referential in referentials:
        foreign_key = referential[LIBRARY].get_foreign_key()
        if len(documents) > 0:
            result[name] = [document.get(foreign_key) for document in documents]
        else:
            result[name] = foreign_key

    return result


def import_library(library):

    result = __import__(library)
    return result


def get_entities(*rks):
    """
    Get all entities from all referentials.
    """

    result = list()

    for name, referential in referentials:
        result += referential[LIBRARY].get_entities(*rks)

    return result


def get_topologies(*rks):
    """
    Get all topologies from all referentials.
    """

    result = list()

    for name, referential in referentials:
        result += referentials[LIBRARY].get_topologies(*rks)

    return result


def send_entities(*rks):
    """
    Get all entitiesfrom all referentials.
    """

    for name, referential in referentials:
        referentials[LIBRARY].send_entities(*rks)


def update_entities():
    """
    Update the collection entities with a dictionary of referentials which must contain both LIBRARY and BINDING properties.
    """

    # connect to mongo
    connection = pymongo.Connection()
    # get collection entities
    entities_collection = connection.canopsis.entities

    # get all entities from all referentials
    entities = get_entities()

    # upsert entities
    for entity in entities:
        entities_collection.update(
            {'rk': entity.rk},
            {'$set': entity},
            upsert=True,
            safe=True
        )
