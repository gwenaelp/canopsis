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
import logging
logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)

import zlib
import time

import msgpack
packer = None
unpacker = None

import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import *

AVERAGE = 'AVERAGE'
MEAN = 'MEAN'
LAST = 'LAST'
FIRST = 'FIRST'
DELTA = 'DELTA'
SUM = 'SUM'
MAX = 'MAX'
MIN = 'MIN'

T_SECOND = 'second'
T_MINUTE = 'minute'
T_HOUR = 'hour'
T_DAY = 'day'
T_WEEK = 'week'
T_MONTH = 'month'
T_YEAR = 'year'

T_UNITS = [T_SECOND, T_MINUTE, T_HOUR, T_DAY, T_WEEK, T_MONTH, T_YEAR]

VALUE = 'value'
UNIT = 'unit'

MAX_POINTS = 500

class Period(object):
	"""
	Period management with a value and an unit.
	"""
	def __init__(self, value, unit=T_SECOND):
		self.value = value
		self.unit = unit

	def get_delta(self, date, delta=None):
		result = delta

		if (self.unit == T_YEAR or self.unit == T_MONTH) and float.is_integer(self.value):
			# force new delta in case of year or month unit
			if self.unit == T_YEAR:
				days = int(period.value * (366 if calendar.isleap(date.year) else 365))

			else :
				monthrange = calendar.monthrange(date.year, date.month)
				days = int(monthrange[1] * period.value)

			result = timedelta(days=days)

		elif result == None:

			kwargs = {self.unit + 's': self.value}

			if self.unit == T_MONTH or self.unit == T_YEAR:
				result = relativedelta(**kwargs)

			else:
				result = timedelta(**kwargs)

		return result

class TimeWindow(object):
	"""
	Time window management with exclusion intervals.
	Contains a start/stop dates and an array of exclusion intervals (couple of START, STOP timestamp).
	"""
	def __init__(self, start, stop=time.time(), exclusion_intervals=[], max_points=MAX_POINTS, period=None):
		self.start = start
		self.stop = stop
		self.exclusion_intervals = exclusion_intervals
		self.period = self._get_period(max_points, period)
		self.timezone = timezone
		self._delta = None

	def _get_period(self, max_points, period):
		result = period

		if max_points :
			interval = self.stop - self.start
			seconds = interval.total_seconds() / max_points
			result = Period(seconds, T_SECOND)

		return result

	def total_seconds(self):
		delta = self.stop - self.start
		result = delta.total_seconds()
		return result

	def __repr__(self):
		message = "start = %s, stop = %s, exclusion_intervals = %s, period = %s, timezone = %s, current_date = %s"
		result = message % (self.start, self.stop, self.exclusion_intervals, self.period, self.timezone, self.current_date)
		return result

	@staticmethod
	def get_datetime(timestamp, timezone):
		dt = timedelta(seconds=timezone)
		result = datetime.utcfromtimestamp(timestamp) - dt
		return result

	@staticmethod
	def roundtime(utcdate, period, timezone=time.timezone):
		"""
		Calculate roudtime relative to an UTC date, a period time/type and a timezone.
		"""
		result = utcdate

		relativeinterval = intervalToRelativeDelta.get(period.unit)

		dt = timedelta(seconds=timezone)
		result -= dt

		# assume result does not contain seconds and microseconds in this case
		result = result.replace(second=0, microsecond=0)

		if period.unit == T_SECOND:
			seconds = (result.second * 60 / period.value) * period.value / 60
			result = result.replace(second=seconds)

		elif period.unit == T_MINUTE:
			minutes = (result.minute * 60 / period.value) * period.value / 60
			result = result.replace(minute=minutes)

		else:
			result = result.replace(minute=0)

			index_unit = T_UNITS.index(period.unit)

			if index_unit >= T_UNITS.index(T_DAY): # >= 1 day
				result = result.replace(hour=0)

				if index_unit >= T_UNITS.index(T_WEEK): # >= 1 week

					weeks = calendar.monthcalendar(result.year, result.month)
					for week in weeks:
						if result.day in week:
							result = result.replace(day=week[0] if week[0]!=0 else 1)
							break

				if index_unit >= T_UNITS.index(T_MONTH): # >= 1 month
					result = result.replace(day=1)

					if index_unit >= T_UNITS.index(T_YEAR): # >= 1 year
						result = result.replace(month=1)

		result += dt

		return result

	@staticmethod
	def get_next_date(date, timeWindow, period, delta=None):
		"""
		Get next date of input date with timewindow parameters, period and optionnaly a previous calculated delta.
		"""
		delta = period.get_date(date, delta)
		# check if next date is in exclusion dates of the input timewindow
		result = date + delta
		return result

	@staticmethod
	def get_previous_date(date, timewindow, period, delta=None):
		"""
		Get previous date of input date with timewindow parameters, period and optionnaly a previous calculated delta. 
		"""
		delta = period.get_delta(date, delta)
		# check if next date is in exclusion dates of the input timewindow
		result = date - delta
		return result

#### Utils fn
def datetimeToTimestamp(_date):
	return time.mktime(_date.timetuple())

def get_overlap(a, b):
	return max(0, min(a[1], b[1]) - max(a[0], b[0]))

def delta(points):
	if len(points) == 1:
		return points[0][1]
		
	vfirst = get_first_value(points)
	vlast = get_last_value(points)

	return vlast - vfirst

def median(vlist):
    values = sorted(vlist)
    count = len(values)

    if count % 2 == 1:
        return values[(count+1)/2-1]
    else:
        lower = values[count/2-1]
        upper = values[count/2]

    return (float(lower + upper)) / 2

def get_timestamp_interval(points):
	timestamp = 0
	timestamps = []
	for point in points:
		timestamps.append(point[0] - timestamp)
		timestamp = point[0]

	if len(timestamps) > 1:
		del timestamps[0]

	return int(median(timestamps))

def get_timestamps(points):
	return [x[0] for x in points]

def get_values(points):
	return [x[1] for x in points]

def derivs(vlist):
	return [vlist[i] - vlist[i - 1] for i in range(1, len(vlist) - 2)]

def parse_dst(points, dtype, first_point=[]):
	logger.debug("Parse Data Source Type %s on %s points" % (dtype, len(points)))

	dtype = dtype.upper()
		
	if dtype == "DERIVE" or dtype == "COUNTER" or dtype == "ABSOLUTE":
		if points:
			rpoints = []
			values = get_values(points)
			i=0
			last_value=0
			counter = 0
			
			logger.debug('There is %s values' % len(values))
			
			for point in points:
				
				value = point[1]
				timestamp = point[0]
				
				previous_timestamp = None
				previous_value = None
				
				## Get previous value and timestamp
				if i != 0:
					previous_value 		= points[i-1][1]
					previous_timestamp	= points[i-1][0]
				elif i == 0 and first_point:
					previous_value		= first_point[1]
					previous_timestamp	= first_point[0]
				
				
				## Calcul Value
				if dtype != "COUNTER":
					if previous_value:
						if value > previous_value:
							value -= previous_value
						else:
							value = 0
				
				## Derive
				if previous_timestamp and dtype == "DERIVE":	
					interval = abs(timestamp - previous_timestamp)
					if interval:
						value = round(float(value) / interval, 3)
				
				## Abs
				if dtype == "ABSOLUTE":
					value = abs(value)
					
				## COUNTER
				if dtype == "COUNTER":
					value = value + counter
					counter = value

				## if new dca start, value = 0 and no first_point: wait second point ...
				if dtype == "DERIVE" and i == 0 and not first_point:
					## Drop this point
					pass
				else:
					rpoints.append([timestamp, value])
					
				i += 1
				
			return rpoints
	
	return points

def getTimeSteps(timewindow, roundtime, timezone=time.timezone):
	logger.debug('getTimeSteps:')

	timeSteps = []
	
	logger.debug('   + TimeWindow: %s' % timewindow)

	start_datetime 	= datetime.utcfromtimestamp(timewindow.start)
	stop_datetime 	= datetime.utcfromtimestamp(timewindow.stop)

	if roundtime:
		stop_datetime = TimeWindow.roundTime(stop_datetime, timewindow.period, timezone)

	date = stop_datetime
	start_delta = timewindow.period.get_delta(start_datetime)
	start_datetime_minus_delta = start_datetime - start_delta

	date_delta = timewindow.period.get_delta(date)

	while date > start_datetime_minus_delta:
		ts = calendar.timegm(date.timetuple())
		timeSteps.append(ts)
		date_delta = timewindow.period.get_delta(date, date_delta)
		date -= date_delta
	
	timeSteps.reverse()
	
	logger.debug('   + timeSteps: ', timeSteps)

	return timeSteps

def get_operation(name):
	"""
	Get an operation related to an input name.
	"""

	if name == MEAN or not name:
		result = lambda x: sum(x) / float(len(x))
	elif name == MIN:
		result = lambda x: min(x)
	elif name == MAX:
		result = lambda x: max(x)
	elif name == FIRST:
		result = lambda x: x[0]
	elif name == LAST:
		result = lambda x: x[-1]
	elif name == DELTA:
		result = lambda x: (max(x) - min(x)) / 2.0

	return result

def aggregate(points, timewindow, atype=AVERAGE, agfn=None, fill=False, roundtime=True, timezone=time.timezone):
	
	logger.debug("Aggregate %s points (timewindow: %s, max: %s, period: %s, method: %s, fill: %s, roundtime: %s, timezone: %s)" % (len(points), timewindow, max_points, period, atype, fill, roundtime, timezone))

	if not agfn:
		agfn = get_operation(atype)

	rpoints=[]
	
	if len(points) == 1:
		return [ [timewindow.start, points[0][1]] ]
		
	timeSteps = getTimeSteps(timewindow, roundtime, timezone)

	#initialize variables for loop
	prev_point = None
	i=0
	points_to_aggregate = []
	last_point = None

	for index in xrange(1, len(timeSteps)):

		timestamp = timeSteps[index]
			
		previous_timestamp = timeSteps[index-1]
			
		logger.debug("   + Interval %s -> %s" % (previous_timestamp, timestamp))

		while i < len(points) and points[i][0] < timestamp:

			points_to_aggregate.append(points[i])

			i+=1

		if atype == 'DELTA' and last_point:
			points_to_aggregate.insert(0, last_point)

		aggregation_point = get_aggregation_point(points_to_aggregate, agfn, previous_timestamp, fill)

		rpoints.append(aggregation_point)

		if points_to_aggregate:
			last_point = points_to_aggregate[-1]

		points_to_aggregate = []

	if i < len(points):

		points_to_aggregate = points[i:]

		if atype == 'DELTA' and last_point:
			points_to_aggregate.insert(0, last_point)

		aggregation_point = get_aggregation_point(points_to_aggregate, agfn, timeSteps[-1], fill)

		rpoints.append(aggregation_point)

	logger.debug(" + Nb points: %s" % len(rpoints))

	return rpoints

def get_aggregation_point(points_to_aggregate, fn, timestamp, fill):
	if points_to_aggregate:
		
		logger.debug("     + %s points to aggregate" % (len(points_to_aggregate)))

		agvalue = round(fn(points_to_aggregate), 2)

		result = [timestamp, agvalue]

	else:
		logger.debug("       + No points")

		result = [timestamp, 0 if fill else None]

	logger.debug("   + Point : %s " % result)

	return result

def compress(points):
	logger.debug("Compress timeserie")
	
	# Create packer
	global packer
	if not packer:
		packer = msgpack.Packer()
	
	# Remplace timestamp by interval
	logger.debug(" + Remplace Timestamp by Interval and compress it")
	i = 0
	fts = points[0][0]
	offset = points[0][0]
	previous_interval = None

	data = []
	
	logger.debug(" + FTS: %s" % fts)

	for point in points:
		timestamp = point[0]
		value = point[1]
		
		# If int, dont store float
		if value == int(value):
			value = int(value)
	
		if i == 0:
			# first point
			interval = timestamp - offset
			data.append(value)
		else:
			# Others
			interval = timestamp - offset
			if interval == previous_interval:
				data.append(value)
			else:
				previous_interval = interval
				data.append([interval, value])

		#logger.debug("    + %s: %s: %s" % (i, point, data[i]))
		
		offset = timestamp
		i += 1
	
	data = (fts, data)
	# Pack and compress points
	
	points = zlib.compress(packer.pack(data), 9)

	return points

def uncompress(data):
	logger.debug("Uncompress timeserie")
	
	if not data:
		raise ValueError("Invalid data type (%s)" % type(data))

	# Create unpacker
	global unpacker
	if not unpacker:
		unpacker = msgpack.Unpacker(use_list=True)
	
	unpacker.feed(str(zlib.decompress(data)))
	data = unpacker.unpack()
	
	fts = data[0]
	points = data[1]
	
	logger.debug(" + Type of point: %s" % type(points))
	
	if type(points).__name__ != 'list':
		raise ValueError("Invalid type (%s)" % type(points))
	
	rpoints = []

	#first point
	rpoints.append([fts, points[0]])
	logger.debug("   + First point: %s" % (rpoints[0]))

	#second point
	offset = points[1][0]
	timestamp = fts + offset
	rpoints.append([timestamp, points[1][1]])
	
	logger.debug("   + Second point: %s" % (rpoints[1]))
	
	logger.debug(" + Offset: %s", offset)

	#others
	for i in range(2, len(points)):
		point = points[i]
		
		if isinstance(point ,list) or isinstance(point ,tuple):
			offset = point[0]
			#logger.debug(" + Offset: %s", offset)
			timestamp += offset
			rpoints.append([ timestamp, point[1] ])
		else:
			timestamp += offset
			rpoints.append([ timestamp, point ])
			
		#logger.debug("  %i -> %s" % (i, rpoints[i]))
	
	return rpoints

### aggregation serie function
def consolidation(series, fn, interval=None):
	
	# Todo calcul interval
	if not interval:
		interval = 300

	# Find start and stop ts
	start = None
	stop = None
	for serie in series:
		timestamps = [point[0] for point in serie]
		smin = min(timestamps)
		smax = max(timestamps)
		if start == None or smin < start:
			start = smin
		if stop == None or smax > stop:
			stop = smax

	# Align timestamps
	nseries = []
	for serie in series:
		ts = start
		index = 0
		nserie = []
		last_value = None

		while ts <= stop:
			while index < len(serie) and serie[index][0] <= ts:
				last_value = serie[index][1]
				index += 1

			nserie.append( (ts, last_value) )
			ts+=interval

		nseries.append(nserie)

	# Do operations
	result = []
	ts = start
	i = 0
	while ts <= stop:
		points = []
		for serie in nseries:
			if serie[i][1]:
				points.append(serie[i][1])

		value = fn(points)
		result.append((ts, value))

		i  += 1
		ts += interval

	return result

def holtwinters(y, alpha=0.99, beta=0.12, gamma=0.80, c=0, debug=True):
    """
    y - time series data.
    alpha(0.2) , beta(0.1), gamma(0.05) - exponential smoothing coefficients 
                                      for level, trend, seasonal components.
    c -  extrapolated future data points.
          4 quarterly
          7 weekly.
          12 monthly

    The length of y must be a an integer multiple (> 2) of c.
    """
    logger.debug("y = %s, alpha = %s, beta = %s, gamma = %s, c = %s" % (y, alpha, beta, gamma, c))

    #Compute initial b and intercept using the first two complete c periods.
    ylen =len(y)

    if not c:
		c = ylen >> 1

    if ylen % c !=0:
        return None

    fc =float(c)

    ybar2 =sum([y[i] for i in range(c, 2 * c)])/ fc
    ybar1 =sum([y[i] for i in range(c)]) / fc
    b0 =(ybar2 - ybar1) / fc
    logger.debug("b0 = ", b0)

    #Compute for the level estimate a0 using b0 above.
    tbar = ((c * (c + 1)) >> 1) / fc
    logger.debug("tbar = ", tbar)
    a0 = ybar1 - b0 * tbar
    logger.debug("a0 = ", a0)

    #Compute for initial indices
    I = [y[i] / (a0 + (i + 1) * b0) for i in range(0, ylen)]
    logger.debug("Initial indices = ", I)

    S = [0] * (ylen + c)
    for i in range(c):
        S[i] =(I[i] + I[i+c]) / 2.0

    #Normalize so S[i] for i in [0, c)  will add to c.
    tS = c / sum([S[i] for i in xrange(c)])
    for i in xrange(c):
        S[i] *= tS
        logger.debug("S[",i,"]=", S[i])

    # Holt - winters proper ...
    logger.debug("Use Holt Winters formulae")
    F = [0] * (ylen + c)

    At = a0
    Bt = b0
    for i in xrange(ylen):
        Atm1 = At
        Btm1 = Bt
        At = alpha * y[i] / S[i] + (1.0 - alpha) * (Atm1 + Btm1)
        Bt = beta * (At - Atm1) + (1 - beta) * Btm1
        S[i + c] = gamma * y[i] / At + (1.0 - gamma) * S[i]
        F[i] = (a0 + b0 * (i + 1)) * S[i]
        logger.debug("i=", i + 1, "y=", y[i], "S=", S[i], "Atm1=", Atm1, "Btm1=",Btm1, "At=", At, "Bt=", Bt, "S[i+c]=", S[i+c], "F=", F[i])
    #Forecast for next c periods:
    for m in xrange(c):
        F[ylen + m] = (At + Bt * (m + 1)) * S[ylen + m]
        logger.debug("forecast:", F[ylen + m])

    logger.debug("F = ", F)

    return F

def forecast(points, period, max_points, alpha=0.99, beta=0.12, gamma=0.80):

	if not points:
		return points

	y = [point[1] for point in points]

	F = holtwinters(y, alpha, beta, gamma, max_points)

	result = [ [z[0][0], z[1]] for z in zip(points, F[:len(points)])]

	rd = get_relativedelta(period)

	for index in xrange(len(points), len(F)):
		timestamp = get_nexttimestamp(rd, result[index-1][0])
		point = [timestamp, F[index]]
		result.append(point)

	return result
