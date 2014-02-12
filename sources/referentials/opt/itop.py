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
Canopsis Referential interface.
"""

import requests
import json
import pymongo
import clogging

logger = clogging.getLogger()

# ITOP specific fields
OPERATION = 'operation'
KEY = 'key'
CLASS = 'class'
CANOPSIS_ITEM = 'CanopsisItem'
APPLICATION_SOLUTION = 'ApplicationSolution'

# HTTP
HTTP_OK = 200

# CanopsisItem key in ITOP
KEY_ITOP = 'key_itop'


def get_foreign_key():
    """
    Get documents foreign key. None if it does not exist.
    If documents is Empty, returns itop foreign key.
    """
    result = KEY_ITOP

    if len(documents) > 0:
        result = [document.get(KEY_ITOP) for document in documents]

    return result


def get_payload(json_data):
    """
    Generate a payload related to input operation.
    """

    result = {
        'auth_user': 'admin',
        'auth_pwd': 'admin',
        'version': "1.0",
        'json_data': json.dumps(json_data)
    }

    return result


def do_request(binding, json_data):
    """
    Execute a request and returns the result.
    """

    payload = get_payload(json_data)
    result = requests.get(binding, params=payload)

    return result


def get_items(binding, operation, clazz, oql_request, additional_fields=None):
    """
    Get items with an OQL request.
    """

    operations = {
        OPERATION: operation,
        CLASS: clazz,
        KEY: oql_request
    }

    if additional_fields is not None:
        operations.update(additional_fields)

    response = do_request(binding, operations)

    if response.status_code == HTTP_OK:
        response = json.loads(response.text)
        objects, relations = response.get('objects'), response.get('relations')
        result = list(), list()
        for name, object in objects.iteritems():
            object[KEY_ITOP] = name
            result[0].append(object)
        for name, relation in relations.iteritems():
            result[1].append(relation)

    else:
        raise Exception(result)
        result = None

    return result


def get_entities(binding):
    """
    Get Canopsis entities.
    """

    result = get_items(binding, 'core/get', CANOPSIS_ITEM, 'SELECT CanopsisItem')

    return result


def get_csvs(binding):
    """
    TODO
    """

    def get_primary_key(entity):
        """
        Get input entity primary key.
        """

        result = "{0}:{1}:{2}:".format(entity['connector'], entity['connector_name'])

        component = entity.get('component')
        if component is not None:
            result += "{0}:".format(component)

        result += entity['name']

        return result

    entities = pymongo.Connection().canopsis.entities

    components, resources = list(), list()

    # find entities components
    entities = entities.find(
        {'type': {'$in': ['component', 'resource']}},
        {
            'connector_name': 1,
            'connector': 1,
            'name': 1,
            'type': 1,
            'component': 1
        }
    )

    component_fields = ['primary_key', 'org_id', 'connector', 'connector_name', 'name']
    resource_fields = ['primary_key', 'canopsis_component_id', 'name']

    csv_components = reduce(lambda x, y: x+y, component_fields)
    csv_components += '\n'

    csv_resources = reduce(lambda x, y: x+y, resource_fields)
    csv_resources += '\n'

    # send resources in filling csv files
    for entity in entities:

        if entity['crecord_type'] == 'component':
            fields = component_fields
            csv = csv_components
        else:
            fields = resource_fields
            csv = csv_resources

        primary_key = get_primary_key(entity)
        csv += "{0};".format(primary_key)

        for field in fields:
            csv += "{0};".format(entity[field])

    return csv_components, csv_resources


def send_entities(binding):
    """
    TODO: Send entities to an itop referential.
    """

    components, resources = get_csvs(binding)


def get_topologies(binding):
    """
    Get topologies.
    """

    additional_fields = {
        'relation': 'depends on',
        'depth': 4
    }

    topologies = get_items(
        binding,
        'core/get_related',
        APPLICATION_SOLUTION,
        'SELECT ApplicationSolution',
        additional_fields)

    for topology in topologies:
        pass

    return topologies

import sys

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) == 2:
        result = globals()[args[0]](args[1])
        print(result)
    else:
        print("Wait for a method and a binding argument")
