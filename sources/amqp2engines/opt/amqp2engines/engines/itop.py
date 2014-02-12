#!/usr/bin/env python
#--------------------------------
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
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

from cengine import cengine
from cstorage import get_storage
from caccount import caccount

import time, json, logging, pprint, io, csv

import requests

NAME="itop"

class engine(cengine):

	def __init__(self, *args, **kargs):
		cengine.__init__(self, name=NAME, *args, **kargs)
		self.nb_beat = 0
		self.beat_interval = 10

	def pre_run(self):
		#load selectors
		self.storage = get_storage(namespace='object', account=caccount(user="root", group="root"))
		self.beat()


	def beat(self):
		self.logger.debug('entered in selector BEAT')
		self.extract_csv('entities')

		operation = {
		   'operation'		: 'core/get',
		   'class'			: 'CanopsisItem',
		   'key'			: 'SELECT CRM',
		   'output_fields'	: '*'
		}

		response = self.query_api('192.168.0.15', operation)
		if response:
			pp = pprint.PrettyPrinter(indent=2)
			self.logger.debug(pp.pformat(response))


	def triggerItopSync(self):
		# TODO
		self.logger.info('Will trigger itop sync')
		pass

	def extract_csv(self, extract_type):

		filename = '/tmp/itop_metas.csv'

		f = open(filename, 'w')
		writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)

		collection = self.storage.get_backend(extract_type)

		extract_keys = {'entities': ['component','resource','connector_name','crecord_name', 'crecord_type']}[extract_type]
		headers = ['primary_key'] + extract_keys[:] + ['org_id']

		writer.writerow(headers)

		count_pass = 0

		for document in collection.find({}, {key:1 for key in extract_keys}, limit=100):

			line = ''
			values = []
			for key in extract_keys:
				if key in document and document[key]:
					values.append(str(document[key]))
				else:
					self.logger.debug('missing > ' + key)
					count_pass += 1
					break
			if len(values) == len(extract_keys):
				# Add primary key and org _id
				values = ['%s_%s' % (document['component'], document['resource'])] + values + ['Demo']
				writer.writerow(values)

		self.logger.debug("was unable to serialize %s items" % (count_pass))
		self.logger.info("written csv file %s" % (filename))

		f.close()


	def query_api(self, adress, operation):

		url = 'http://%s/itop/webservices/rest.php?version=1.0' % (adress)

		# Json query core stringified in HTTP call
		try:
			operation = json.dumps(operation)
		except Exception, e:
			self.logger.error('unable to parse itop API query')

		# Document operation
		query = {
			'auth_pwd': 'admin',
			'auth_user': 'admin',
			'json_data' : operation
		}

		# effective HTTP query
		headers = {'content-type':'application/json'}
		r = requests.post(url, params=query, headers=headers)

		response = None

		try:
			response = json.loads(r.text)
			self.logger.info('Got itop API response will process response')
		except Exception, e:
			self.logger.error('unable to read itop API response %s' % (str(e)))

		return response

