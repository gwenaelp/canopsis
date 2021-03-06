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

import time

from copy import deepcopy

from cengine import cengine
import cevent

from cstorage import get_storage
from caccount import caccount
import pyperfstore2

import logging

NAME="alertcounter"
INTERNAL_COMPONENT = '__canopsis__'
PROC_CRITICAL = 'PROC_CRITICAL'
PROC_WARNING = 'PROC_WARNING'

class engine(cengine):
	def __init__(self, *args, **kargs):
		super(engine, self).__init__(name=NAME, *args, **kargs)

	def pre_run(self):
		self.listened_event_type = ['check','selector','eue','sla', 'log']
		self.manager = pyperfstore2.manager()

		# Get SLA configuration
		self.storage = get_storage(namespace='object', account=caccount(user="root", group="root"))
		self.entities = self.storage.get_backend('entities')

		self.selectors_name = []
		self.last_resolv = 0
		#last sla is for testing purposes
		self.last_sla_state = None
		self.beat()

	def load_macro(self):
		self.logger.debug('Load record for macros')

		self.mCrit = PROC_CRITICAL
		self.mWarn = PROC_WARNING

		record = self.storage.find_one({'crecord_type': 'slamacros'})

		if record:
			self.mCrit = record.data['mCrit']
			self.mWarn = record.data['mWarn']

	def load_crits(self):
		self.logger.debug('Load records for criticalness')

		self.crits = {}

		records = self.storage.find({'crecord_type': 'slacrit'})

		for record in records:
			self.crits[record.data['crit']] = record.data['delay']

	def beat(self):
		self.load_macro()
		self.load_crits()

	def perfdata_key(self, meta):
		if 're' in meta and meta['re']:
			return '{0}{1}{2}'.format(meta['co'], meta['re'], meta['me'])

		else:
			return '{0}{1}'.format(meta['co'], meta['me'])

	def increment_counter(self, meta, value):
		key = self.perfdata_key(meta)
		self.logger.debug("Increment {0}: {1}".format(key, value))
		self.logger.debug(str(meta))
		self.manager.push(name=key, value=value, meta_data=meta)

	def update_global_counter(self, event):
		# Comment action (ensure the component exists in database)
		logevent = cevent.forger(
			connector = 'cengine',
			connector_name = NAME,
			event_type = 'log',
			source_type = 'component',
			component = INTERNAL_COMPONENT,

			output = 'Updating global counter'
		)

		self.amqp.publish(logevent, cevent.get_routingkey(logevent), self.amqp.exchange_name_events)

		# Update counter
		new_event = deepcopy(event)
		new_event['connector']      = 'cengine'
		new_event['connector_name'] = NAME
		new_event['event_type']     = 'check'
		new_event['source_type']    = 'component'
		new_event['component']      = INTERNAL_COMPONENT

		if 'resource' in new_event:
			del new_event['resource']

		self.count_alert(new_event, 1)

		logevent['source_type'] = 'resource'
		new_event['source_type'] = 'resource'

		for hostgroup in event.get('hostgroups', []):
			logevent['resource'] = hostgroup
			new_event['resource'] = hostgroup

			self.count_alert(new_event, 1)

			self.amqp.publish(logevent, cevent.get_routingkey(logevent), self.amqp.exchange_name_events)

	def count_sla(self, event, slatype, slaname, delay, value):
		meta_data = {'type': 'COUNTER', 'co': INTERNAL_COMPONENT }
		now = int(time.time())
		#last_state_change field is updated in event store, so here we have no real previous date
		if 'previous_state_change_ts' in event:
			compare_date = event['previous_state_change_ts']
		else:
			compare_date = event['last_state_change']

		if delay < (now - compare_date):
			ack = self.entities.find_one({
				'type': 'ack',
				'timestamp': {
					'$gt': event['last_state_change'],
					'$lt': event['previous_state']
				}
			})

			self.last_sla_state = 'nok' if ack else 'out'
			meta_data['me'] = 'cps_sla_{0}_{1}_{2}'.format(
				slatype,
				slaname,
				self.last_sla_state
			)

		else:
			meta_data['me'] = 'cps_sla_{0}_{1}_ok'.format(slatype, slaname)

		self.increment_counter(meta_data, value)

	def count_by_crits(self, event, value):
		if event['state'] == 0 and event.get('state_type', 1) == 1:
			warn = event.get(self.mWarn, None)
			crit = event.get(self.mCrit, None)

			if warn and warn in self.crits and event['previous_state'] == 1:
				self.count_sla(event, 'warn', warn, self.crits[warn], value)

			elif crit and crit in self.crits and event['previous_state'] == 2:
				self.count_sla(event, 'crit', crit, self.crits[crit], value)

			# Update others
			meta_data = {'type': 'COUNTER', 'co': INTERNAL_COMPONENT }

			for _crit in self.crits:
				# Update warning counters
				if _crit != warn:
					for slatype in ['ok', 'nok', 'out']:
						meta_data['me'] = 'cps_sla_warn_{0}_{1}'.format(_crit, slatype)
						self.increment_counter(meta_data, 0)

				# Update critical counters
				if _crit != crit:
					for slatype in ['ok', 'nok', 'out']:
						meta_data['me'] = 'cps_sla_crit_{0}_{1}'.format(_crit, slatype)
						self.increment_counter(meta_data, 0)

	def count_alert(self, event, value):
		component = event['component']
		resource = event.get('resource', None)
		tags = event.get('tags', [])
		state = event['state']
		state_type = event.get('state_type', 1)

		# Update cps_statechange{,_0,_1,_2,_3} for component/resource

		meta_data = {
			'type': 'COUNTER',
			'co': component,
			'tg': tags
		}

		if resource:
			meta_data['re'] = resource

		meta_data['me'] = "cps_statechange"
		self.increment_counter(meta_data, value)

		meta_data['me'] = "cps_statechange_nok"
		cvalue = value if state != 0 else 0
		self.increment_counter(meta_data, cvalue)

		for cstate in [0, 1, 2, 3]:
			cvalue = value if cstate == state else 0

			meta_data['me'] = "cps_statechange_{0}".format(cstate)
			self.increment_counter(meta_data, cvalue)

		# Update cps_statechange_{hard,soft}

		for cstate_type in [0, 1]:
			cvalue = value if cstate_type == state_type and state != 0 else 0

			meta_data['me'] = "cps_statechange_{0}".format(
				'hard' if cstate_type == 1 else 'soft'
			)

			self.increment_counter(meta_data, cvalue)

	def count_by_type(self, event, value):
		state = event['state']

		#Shortcut
		def increment(increment_type, value):
			self.increment_counter({
				'type': 'COUNTER',
				'co': INTERNAL_COMPONENT,
				'tg': event.get('tags', []),
				'me': "cps_statechange_{0}".format(increment_type)
			}, value)

		#Keep only logic. increment component if on error
		if event['source_type'] == 'component':
			if state != 0:
				increment('component', value)
			else:
				increment('component', 0)

		# increment resource if in error. status depends on it s component. increment resource by component if in error by component
		if event['source_type'] == 'resource':

			component_problem = False
			if cevent.is_component_problem(event):
				component_problem = True
				increment('resource_by_component', value)
			else:
				increment('resource_by_component', 0)

			if state != 0 or component_problem:
				increment('resource', value)
			else:
				increment('resource', 0)

		meta_data = {
			'type': 'COUNTER',
			'co': INTERNAL_COMPONENT,
			'tg': event.get('tags', [])
		}
		# Update cps_alerts_not_ack

		if state != 0:
			meta_data['me'] = 'cps_alerts_not_ack'
			self.increment_counter(meta_data, 1)

			meta_data['me'] = 'cps_alerts_ack'
			self.increment_counter(meta_data, 0)

			meta_data['me'] = 'cps_alerts_ack_by_host'
			self.increment_counter(meta_data, 0)

	def resolve_selectors_name(self):

		if int(time.time()) > (self.last_resolv + 60):

			records = self.storage.find(mfilter={'crecord_type': 'selector'}, mfields=['crecord_name'])

			self.selectors_name = [record['crecord_name'] for record in records]

			self.last_resolv = int(time.time())

		return self.selectors_name

	def count_by_tags(self, event, value):
		if event['event_type'] != 'selector':
			tags = event.get('tags', [])
			tags = [tag for tag in tags if tag in self.resolve_selectors_name()]

			for tag in tags:
				self.logger.debug("Increment Tag: '%s'" % tag)
				tagevent = deepcopy(event)
				tagevent['component'] = tag
				tagevent['resource'] = 'selector'

				self.count_alert(tagevent, value)

	def work(self, event, *args, **kargs):
		validation = event['event_type'] in self.listened_event_type
		validation = validation and event['component'] not in ['derogation', INTERNAL_COMPONENT]

		if validation:
			self.update_global_counter(event)
			self.count_by_crits(event, 1)

			# By name
			self.count_alert(event, 1)

			# By Type and ACK
			self.count_by_type(event, 1)

			# By tags (selector)
			self.count_by_tags(event, 1)

		return event
