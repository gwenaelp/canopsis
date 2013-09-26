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
from caccount import caccount
from cstorage import get_storage
#from pyperfstore import node
#from pyperfstore import mongostore
import pyperfstore2
import cevent
import logging

import time
from datetime import datetime

import timeSerie

states_str = ("Ok", "Warning", "Critical", "Unknown")
states = {0: 0, 1:0, 2:0, 3:0}

NAME = 'timeSeriePredicator'

class engine(cengine):

	TIME_WINDOW = 'timeWindow',

	REAL = 'real',
	FORECAST = 'forecast',
	TIME = 'time',

	VALUE = 'value',
	CRITICAL_TRESHOLD = 'critical_treshold',
	WARNING_TRESHOLD = 'warning_treshold',

	START = 'start', 
	STOP = 'stop',
	FREQUENCY = 'frequency',

	HOST = 'host',
	KIND = 'kind',

	ALPHA = 'alpha',
	BETA = 'beta',
	GAMA = 'gama',

	def __init__(self, *args, **kargs):
		cengine.__init__(self, name=NAME, *args, **kargs)
		
		self.create_queue = False
				
		self.beat_interval =  60
		
		# For debug
		#self.beat_interval =  60
		
		self.resource = "timeSeriePredicator"
		
		self.thd_warn_sla_timewindow = 98
		self.thd_crit_sla_timewindow = 95
		self.default_sla_timewindow = 60*60*24 # 1 day
		
		self.default_sla_output_tpl="{cps_pct_by_state_0}% Ok, {cps_pct_by_state_1}% Warning, {cps_pct_by_state_2}% Critical, {cps_pct_by_state_3}% Unknown"

	def pre_run(self):
		self.storage = get_storage(namespace='object', account=caccount(user="root", group="root"))
		self.manager = pyperfstore2.manager(logging_level=self.logging_level)
		self.beat()
	
	def _get_time_delta(self, stime):
		time_delta = None
		if stime['type'] == 's':
			time_delta = datetime.timedelta(secondes=stime['value'])
		elif stime['type'] == 'mn':
			time_delta = datetime.timedelta(minutes=stime['value'])
		elif stime['type'] == 'hr':
			time_delta = datetime.timedelta(hours=stime['value'])
		elif stime['type'] == 'd':
			time_delta = datetime.timedelta(days=stime['value'])
		elif stime['type'] == 'w':
			time_delta = datetime.timedelta(weeks=stime['value'])
		return time_delta

	def _get_period(self, timeWindow, period_key, period_function):
		time_delta = self._get_time_delta(timeWindow[period_key])
		if time_delta == None:
			raise Exception('timeWindow[\'%s\'] : %s is not a value among {s, mn, h, d, m, y}' % (period_key, timeWindow[period_key]))
		period = period_function(time_delta)
		return period

	def _get_start_period(self, timeWindow):
		return self._get_period(timeWindow, engine.START, 
					lambda(time_delta): time.mktime(((datetime.today() - time_delta).timetuple())))

	def _get_stop_period(self, timeWindow):
		return self._get_period(timeWindow, engine.STOP, 
					lambda(time_delta):time.mktime(((datetime.today() + time_delta).timetuple())))

	def _get_frequency(self, timeWindow):
		return self._get_period(timeWindow, engine.FREQUENCY, lambda(time_delta): time_delta.total_seconds())
	
	def get_timeWindow(self, timeWindow):
		start_period = self._get_start_period(timeWindow)
		stop_period = self._get_stop_period(timeWindow)
		frequency = self._get_frequency(timeWindow)
		return {engine.START: start_period, engine.STOP: stop_period, engine.FREQUENCY: frequency}

	def _get_points(self, config, timeWindow):
		metric_name = '%s-%s' % (config[engine.HOST], config[engine.KIND])
		fmetric_name = '%s-f' % metric_name

		points = []
		fpoints = []
		try:
			points = self.manager.get_points(name=metric_name, tstart=timeWindow[engine.START])
			fpoints = self.manager.get_points(name=fmetric_name, tstart=timeWindow[engine.START], tstop=timeWindow[engine.STOP])
		except: 
			return [], []

		return {engine.REAL: points, engine.FORECAST: fpoints}
		
	def get_rk(self, name):
		return "timeSerie.engine.timeSerie.resource.%s.timeSerie" % name
		
	def get_name(self,name):
		return '%stimeSerie' % name

	def _fire_critical_treshold(self, new_point):
		pass	

	def _check_critical_treshold(self, config, new_point):
		if config[CRITICAL_TRESHOLD] <= new_point[engine.VALUE]:
			self._fire_critical_treshold(new_point)

	def _get_warning_treshold(self, config, lower_point, upper_point):
		return config[WARNING_TRESHOLD]

	def _fire_warning_treshold(self, config, y0, y1):
		pass

	def _check_warning_treshold(self, config, new_point, lower_point, upper_point):
		warning_treshold = self._get_warning_treshold(config, lower_point, upper_point)
		y0 = lower_point[engine.VALUE]
		y1 = new_point[engine.VALUE]
		if new_point[engine.TIME] > lower_point[engine.TIME]:
			a = (upper_point[engine.VALUE] - lower_point[engine.VALUE]) / (upper_point[engine.TIME] - lower_point[engine.TIME])
			b = (lower_point[engine.VALUE] - (a * lower_point[engine.TIME]))
			
			y0 = a * new_point[engine.TIME] + b 
		if y1 > (y0 + warning_treshold):
			self._fire_warning_treshold(config, y0, y1)

	def _check_treshold(self, config, last_real_point, new_points, forecasts):
		if len(forecasts) < 0:
			return 
		i_forecast = 0
		# iterate on new_point list
		for new_point in new_points:
			self._check_critical_treshold(config, new_point)
			# find first forecast which is greater or equal to new_point
			while i_forecast < len(forecasts) and new_point[engine.TIME] >= forecasts[i_forecast][engine.TIME]:
				i_forecast += 1
			lower_point, upper_point = None, None
			if i_forecast == 0: # check treshold between last_real_point and firest forecast
				lower_point, upper_point = last_real_point, forecasts[0]				
			elif i_forecast < len(forecasts): # if new_point is between two forecasts
				lower_point, upper_point = forecasts[i_forecast], forecasts[i_forecast+1]
			else: # if new_point appears after last forecast
				continue
			# check warning treshold for new_point between lower_point and upper_point
			self._check_warning_treshold(config, new_point, lower_point, upper_point)

	def _get_forecasts(self, config, timeWindow, points):	
		timeSerie.forecast(points, config[engine.ALPHA], config[engine.BETA], config[engine.GAMA], period, m)
		return []

	def _calculate_forecast(self, _id, config):
		timeWindow = self.get_timeWindow(config)
		
		cd_points = get_points(config, timeWindow)
	
		graph_points = get_graph_points(config)

		new_points = []

		# get last point and identify every last point from last checked and new checked
		if len(graph_points)>0:
			last_point = graph_points[engine.REAL][-1]
			new_points = [point for point in cd_points if point[engine.TIME]>last_point[engine.TIME]]

		# are there new points in the function
		if len(new_points)>0:
			# for every new point, check if they don't exceed forecasted points
			i_forecast = 0
			# find first forecast point where time is less or equal to first new point
			for forecast in graph_points[engine.FORECAST]:
				if forecast[engine.TIME]>=new_points[0][engine.TIME]:
					break
				else:
					i_forecast+=1
			# check if new points are under tersholds
			for new_point in new_points:
				if new_point[engine.TIME]<forecast[i_forecast][engine.TIME]:
					pass
			

		# check on all points if one

		# points = 

		#rk = config['rk']
		self.logger.debug(" + Calcul TIME SERIE of '%s'" % rk)

	"""
		sla_timewindow = config.get('sla_timewindow', self.default_sla_timewindow)
		thd_warn_sla_timewindow = config.get('thd_warn_sla_timewindow', self.thd_warn_sla_timewindow)
		thd_crit_sla_timewindow = config.get('thd_crit_sla_timewindow', self.thd_crit_sla_timewindow)
		sla_output_tpl = config.get('sla_output_tpl', self.default_sla_output_tpl)
		sla_timewindow_doUnknown = config.get('sla_timewindow_doUnknown', True)
	"""
		# Prevent empty string
		if not isinstance(sla_timewindow, int):
			self.logger.warning("%s: Invalid 'sla_timewindow': %s" % (_id, sla_timewindow))
			sla_timewindow = self.default_sla_timewindow
		
		if not thd_warn_sla_timewindow:
			thd_warn_sla_timewindow = self.thd_warn_sla_timewindow
		if not thd_crit_sla_timewindow:
			thd_crit_sla_timewindow = self.thd_crit_sla_timewindow
		if sla_output_tpl == "":
			sla_output_tpl = self.default_sla_output_tpl	
			
		thd_warn_sla_timewindow = float(thd_warn_sla_timewindow)
		thd_crit_sla_timewindow = float(thd_crit_sla_timewindow)
		
		# For debug
		#sla_timewindow = 60*60

		self.logger.debug("   + time serie timewindow:    %s" % sla_timewindow)

		stop = int(time.time())
		start = stop - sla_timewindow
		
	
		self.logger.debug("   + time serie doUnknown:     %s" % sla_timewindow_doUnknown)
		self.logger.debug("   + start:             %s (%s)" % (datetime.utcfromtimestamp(start), start))
		self.logger.debug("   + stop:              %s (%s)" % (datetime.utcfromtimestamp(stop), stop))
		
		try:
			points = self.manager.get_points(name="%s%s" % (config['name'], 'cps_state'), tstart=start, tstop=stop, add_prev_point=True, add_next_point=True)
		except Exception, err:
			self.logger.error("Error when 'get_points': %s" % err)
			points = []
		
		self.logger.debug("   + Nb points:         %s" % len(points))
		
		if len(points) < 2:
			self.logger.debug("     + Need more points")
			return
		
		# For Debug
		#points.insert(0, [start-75, 210])
		#points.append([stop+75, 210])

		
		
		first_point = points.pop(0)
		last_point =  points.pop(len(points)-1)
		
		self.logger.debug("   + First point:       %s" % datetime.utcfromtimestamp(first_point[0]))
		self.logger.debug("   + Last point:        %s" % datetime.utcfromtimestamp(last_point[0]))
		self.logger.debug("   + Total:             %s" % (last_point[0] - first_point[0]))
		
		start_undetermined_time =  first_point[0] - start
		stop_undetermined_time = stop - last_point[0]
		
		self.logger.debug("   + Start utime:       %s" % start_undetermined_time)
		if start_undetermined_time < 0:
			self.logger.debug("     + Sample start too soon, adjust timestamp")
			first_point[0] = start
			
		self.logger.debug("   + Stop utime:        %s" % stop_undetermined_time)
		if start_undetermined_time < 0:
			self.logger.debug("     + Sample finish too late, adjust timestamp")
			last_point[0] = stop	
		
		self.logger.debug("   + Total utime:       %s" % (stop_undetermined_time + start_undetermined_time))
		
		states_sum = states.copy()
		total = 0
		
		if sla_timewindow_doUnknown and start_undetermined_time > 0:
			self.logger.debug("     + Set %s seconds to Unknown state" % start_undetermined_time)
			states_sum[3] = start_undetermined_time
			total += start_undetermined_time
		
		(state, state_type, extra) = self.split_state(first_point[1])
		timestamp = first_point[0]
		self.logger.debug("   + Initial State:     %s" % state)
		
		# Sum all duration by state
		for point in points:
			duration = point[0] - timestamp	
			states_sum[state] += duration
			total += duration
			
			(state, state_type, extra) = self.split_state(point[1])
			timestamp = point[0]
			
		# Finish by last point
		duration = last_point[0] - timestamp
		states_sum[state] += duration
		total += duration		
			
		self.logger.debug("   + States sum:        %s" % states_sum)
		self.logger.debug("   + Total:             %s" % total)
		
		# for event
		output_data = {}
		perf_data_array = []
		
		states_pct = states.copy()
		for state in states_sum:
			if states_sum[state] != 0:
				states_pct[state] = round((states_sum[state] * 100)/float(total), 3)
			else:
				states_pct[state] = 0
				
			metric = 'cps_pct_by_state_%s' % state
			output_data[metric] = states_pct[state]
			perf_data_array.append({"metric": metric, "value": states_pct[state], "max": 100, "unit": "%"})
				
		self.logger.debug("   + States pct:        %s" % states_pct)
		
		self.logger.debug("   + Event:")
		
		# Calcul state
		state = 0
		if states_pct[0] < thd_warn_sla_timewindow:
			state = 1
		if states_pct[0] < thd_crit_sla_timewindow:
			state = 2
		
		self.logger.debug("     + State:     %s (%s)" % (states_str[state], state))
		
		## Build Event
		
		# Fill output (for event)
		output = sla_output_tpl
		if output_data:
			for key in output_data:
				output = output.replace("{%s}" % key, str(output_data[key]))
				
		
		self.logger.debug("     + Output:    %s" % output)
		self.logger.debug("     + Perfdata:  %s" % perf_data_array)
		
		# Send AMQP Event
		event = cevent.forger(
			connector = 'timeSerie',
			connector_name = "engine",
			event_type = "timeSerie",
			source_type="resource",
			component=config['name'],
			resource="timeSerie",
			state=state,
			state_type=1,
			output=output,
			long_output="",
			perf_data=None,
			perf_data_array=perf_data_array,
			display_name=config.get('display_name', None)
		)
		
		# Extra fields
		event['selector_id'] = config['_id']
		event['selector_rk'] = config['rk']
		
		rk = self.get_rk(config['name'])
		
		self.logger.debug("Publish event on %s" % rk)
		self.amqp.publish(event, rk, self.amqp.exchange_name_events)
		
		# Update selector record
		self.storage.update(_id, {'sla_timewindow_lastcalcul': stop, 'sla_timewindow_perfdata': perf_data_array, 'sla_state': event['state'], 'sla_rk': rk})
	
	def beat(self):
		start = time.time()
		error = False

		configs = {}
		records = self.storage.find(
				{ 'crecord_type': 'timeSerie',  
				  # time window
				  'timeWindow': {'$exists': True},
				  'past_period': {'$exists': True}, 
				  'past_tperiod': {'$exists': True}, 
				  'future_period': {'$exists': True}, 
				  'future_tperiod': {'$exists': True}, 
				  # number of points to calculate
				  'precision': {'$exists': True},
				  # tresholds
				  'c_treshold': {'$exists': True}, 
				  'w_treshold': {'$exists': True}, # may evolute in warning time treshold
				  # time serie data identifier
				  'kind': {'$exists': True},
				  'host': {'$exists', : True}, 
				  # storage should be calculated ?
				  'enable': True, 
				  # see if required
				  'dosla': {'$in': [ True, 'on'] }, 'dostate': {'$in': [ True, 'on'] }, 'rk': { '$exists' : True } }, 
				namespace="object")
		for record in records:
			configs[record._id] = record.data
			configs[record._id]['name'] = record.name
			configs[record._id]['_id'] =record._id
		
		for _id in configs:
			config = configs[_id]
			self.logger.debug("Load selector '%s' (%s)" % (config['name'], _id))
			
			timeSerie_id = self.calcule_forecast(_id, config)
			
			self.counter_event += 1
				
		self.counter_worktime += time.time() - start
