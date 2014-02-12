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

import time

import logging

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
		csv = self.extract_csv('entities')
		self.logger.debug("Csv generation complete")
		self.logger.debug("\n\n%s" % (csv))
		filename = '/tmp/itop_' + str(int(time.time()))
		f = open(filename, 'w')
		f.write(csv)
		f.close()
		self.triggerItopSync()

	def triggerItopSync(self):
		# TODO
		self.logger.info('Will trigger itop sync')
		pass

	def extract_csv(self, extract_type):

		collection = self.storage.get_backend(extract_type)

		extract_keys = {'entities': [u'component', u'connector_name']}[extract_type]
		headers = {'entities': [u'primary_key', u'name', u'connector', u'org_id']}[extract_type]


		csv = '"%s"\n' % ('";"'.join(headers))
		count_pass = 0

		#TODO remove limit
		for document in collection.find({}, {key:1 for key in extract_keys}, limit=100):
			line = ''
			values = []
			for key in extract_keys:
				if key in document and document[key]:
					values.append(document[key].replace('"',"\""))
			else:
				count_pass += 1

			if len(values) == len(extract_keys):
				line = '"%s_%s";"%s";"%s";"Demo"\n' % (values[0], values[1], values[0], values[1])


			csv += line
		self.logger.debug("was unable to serialize %s events" % (count_pass))

		return csv