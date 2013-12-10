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

import sys
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
from dateutil.relativedelta import relativedelta


class Period(object):
    """
    Period management with a value and an unit.
    """

    SECOND = 'second'
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

    UNITS = [SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, YEAR]

    def __init__(self, value=1, unit=SECOND):
        self.value = value
        self.unit = unit

    def get_delta(self, date, delta=None):

        result = delta

        if (self.unit == Period.YEAR or self.unit == Period.MONTH) and \
                float.is_integer(self.value):

            # force new delta in case of year or month unit
            if self.unit == Period.YEAR:
                days = int(
                    self.value *
                    (366 if calendar.isleap(date.year) else 365))

            else:
                monthrange = calendar.monthrange(date.year, date.month)
                days = int(monthrange[1] * self.value)

            result = timedelta(days=days)

        elif result is None:

            kwargs = {self.unit + 's': self.value}

            if self.unit == Period.MONTH or self.unit == Period.YEAR:
                result = relativedelta(**kwargs)

            else:
                result = timedelta(**kwargs)

        return result


class TimeWindow(object):
    """
    Time window management with exclusion intervals.
    Contains a start/stop dates and an array of exclusion intervals
    (couple of START, STOP timestamp).
    """

    def __init__(self, start, stop=time.time(), exclusion_intervals=[]):
        self.start = start if start else stop - 60 * 60 * 24
        self.stop = stop
        self.exclusion_intervals = exclusion_intervals
        self._get_exclusion_intervals(exclusion_intervals)
        self._delta = None

    def __repr__(self):
        message = "start = %s, stop = %s, exclusion_intervals = %s"
        result = message % (self.start, self.stop, self.exclusion_intervals)
        return result

    def _get_exclusion_intervals(self, exclusion_intervals):
        # should sort and simplify exclusion intervals
        return exclusion_intervals

    def total_seconds(self):
        """
        Returns seconds inside this timewindow.
        """

        delta = self.stop - self.start
        # remove exclusion_intervals
        result = delta.total_seconds()
        return result

    @staticmethod
    def get_datetime(timestamp, timezone=0):
        dt = timedelta(seconds=timezone)
        result = datetime.utcfromtimestamp(timestamp) - dt
        return result

    @staticmethod
    def sliding_time(utcdate, period, timezone=time.timezone):
        """
        Calculate roudtime relative to an UTC date, a period time/type
        and a timezone.
        """
        result = utcdate

        dt = timedelta(seconds=timezone)
        result -= dt

        # assume result does not contain seconds and microseconds in this case
        result = result.replace(second=0, microsecond=0)

        if period.unit == Period.SECOND:
            seconds = (result.second * 60 / period.value) * period.value / 60
            result = result.replace(second=seconds)

        elif period.unit == Period.MINUTE:
            minutes = (result.minute * 60 / period.value) * period.value / 60
            result = result.replace(minute=minutes)

        else:
            result = result.replace(minute=0)

            index_unit = Period.UNITS.index(period.unit)

            if index_unit >= Period.UNITS.index(Period.DAY):
                result = result.replace(hour=0)

                if index_unit >= Period.UNITS.index(Period.WEEK):

                    weeks = calendar.monthcalendar(result.year, result.month)
                    for week in weeks:
                        if result.day in week:
                            result = result.replace(
                                day=week[0] if week[0] != 0 else 1)
                            break

                if index_unit >= Period.UNITS.index(Period.MONTH):
                    result = result.replace(day=1)

                    if index_unit >= Period.UNITS.index(Period.YEAR):
                        result = result.replace(month=1)

        result += dt

        return result

    @staticmethod
    def get_next_date(date, timeWindow, period, delta=None):
        """
        Get next date of input date with timewindow parameters,
        period and optionaly a previous calculated delta.
        """

        delta = period.get_delta(date, delta)
        # check if next date is in exclusion dates of the input timewindow
        result = date + delta
        return result

    @staticmethod
    def get_previous_date(date, timewindow, period, delta=None):
        """
        Get previous date of input date with timewindow parameters,
        period and optionaly a previous calculated delta.
        """

        delta = period.get_delta(date, delta)
        # check if next date is in exclusion dates of the input timewindow
        result = date - delta
        return result


class TimeSerie(object):
    """
    Time serie management. Contain a TimeWindow, a period, a sliding_time,
    an operation and fill property.
    """

    MAX_POINTS = 500

    MEAN = 'MEAN'
    LAST = 'LAST'
    FIRST = 'FIRST'
    DELTA = 'DELTA'
    SUM = 'SUM'
    MAX = 'MAX'
    MIN = 'MIN'

    def __init__(
            self,
            max_points=MAX_POINTS,
            period=None,
            sliding_time=True,
            operation=MEAN,
            fill=False,
            forecast=None):

        self.period = self._get_period(max_points, period)
        self.sliding_time = sliding_time
        self.operation = operation
        self.fill = fill
        self.forecast = Forecast(**forecast)

    def __repr__(self):

        message = "period: %s, sliding_time: %s, operation: %s, fill: %s"
        result = message % \
            (self.period, self.sliding_time, self.operation, self.fill)
        return result

    def _get_period(self, max_points, period):

        result = Period(value=period.value, unit=period.unit) \
            if period is not None else None

        if result is None and max_points:
            interval = self.timewindow.stop - self.timewindow.start
            # may reduce value with timewindow.exclusion_intervals
            seconds = interval.total_seconds() / max_points
            result = Period(value=seconds)

        return result


class Threshold(object):
    """
    Threshold.
    """

    POURCENT = '%'
    KILO = 'Kilo'
    MEGA = 'Mega'
    GIGA = 'Giga'
    TERA = 'Tera'

    def __init__(self, value=10, unit=POURCENT):

        self.value = value
        self.unit = unit

    def _get_value(self, value, operation):

        result = value + self.value

        if self.unit == Threshold.POURCENT:
            delta = self.value * value / 100
        else:
            delta = self.value
            if self.unit == Threshold.KILO:
                delta *= 1000
            elif self.unit == Threshold.MEGA:
                delta *= 1000 * 1000
            elif self.unit == Threshold.GIGA:
                delta *= 1000 * 1000 * 1000
            elif self.unit == Threshold.TERA:
                delta *= 1000 * 1000 * 1000 * 1000

        result = getattr(value, operation)(delta)

        return result

    def get_add_value(self, value=10, unit=POURCENT):

        result = self._get_value(value, unit, '__add__')
        return result

    def get_sub_value(self, value=10, unit=POURCENT):

        result = self._get_value(value, unit, '__sub__')
        return result


class Forecast(object):
    """
    Forecast management.
    """

    ALPHA = 'alpha'
    BETA = 'beta'
    GAMMA = 'gamma'

    DEFAULT_ALPHA = 0.99
    DEFAULT_BETA = 0.12
    DEFAULT_GAMMA = 0.80

    MAX_POINTS = TimeSerie.MAX_POINTS / 2

    NOT_LINEAR_MID_VARIABLE = 'NotLinearMidVariable'
    LINEAR_NOT_VARIABLE = 'LinearNotVariable'
    NOT_LINEAR_VARIABLE = 'NotLinearVariable'
    LINEAR_VARIABLE = 'LinearVariable'

    CURVE_TYPE = 'curve_type'

    NotLinearMidVariable = {
        CURVE_TYPE: NOT_LINEAR_MID_VARIABLE,
        ALPHA: 0.99,
        BETA: 0.12,
        GAMMA: 0.80}
    LinearNotVariable = {
        CURVE_TYPE: LINEAR_NOT_VARIABLE,
        ALPHA: 0.99,
        BETA: 0.01,
        GAMMA: 0.97}
    NotLinearVariable = {
        CURVE_TYPE: NOT_LINEAR_VARIABLE,
        ALPHA: 0.60,
        BETA: 1,
        GAMMA: 0.01}
    LinearVariable = {
        CURVE_TYPE: LINEAR_VARIABLE,
        ALPHA: 0.68,
        BETA: 0.01,
        GAMMA: 0.17}

    PARAMETERS = [
        LinearNotVariable,
        LinearVariable,
        NotLinearVariable,
        NotLinearMidVariable
    ]

    def __init__(
            self,
            timeserie,
            max_points=MAX_POINTS,
            date=None,
            duration=None,
            parameters=NotLinearMidVariable,
            threshold=Threshold()):

        self.timeserie = timeserie
        self.max_points = max_points
        self.date = date
        self.duration = duration
        self.parameters = parameters

    def __repr__(self):
        message = "time_serie: %s, max_pts: %s, \
            date: %s, duration: %s, params: %s"
        result = message % (
            self.timeserie,
            self.max_points,
            self.date,
            self.duration,
            self.parameters)
        return result


def datetimeToTimestamp(_date):
    return time.mktime(_date.timetuple())


def get_overlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


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
    logger.debug(
        "Parse Data Source Type %s on %s points" % (dtype, len(points)))

    dtype = dtype.upper()

    if dtype == "DERIVE" or dtype == "COUNTER" or dtype == "ABSOLUTE":
        if points:
            rpoints = []
            values = get_values(points)
            i = 0
            counter = 0

            logger.debug('There is %s values' % len(values))

            for point in points:

                value = point[1]
                timestamp = point[0]

                previous_timestamp = None
                previous_value = None

                ## Get previous value and timestamp
                if i != 0:
                    previous_value = points[i-1][1]
                    previous_timestamp = points[i-1][0]
                elif i == 0 and first_point:
                    previous_value = first_point[1]
                    previous_timestamp = first_point[0]

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

                ## if new dca starts, value 0 and no first_point wait second pt
                if dtype == "DERIVE" and i == 0 and not first_point:
                    ## Drop this point
                    pass
                else:
                    rpoints.append([timestamp, value])

                i += 1

            return rpoints

    return points


def getTimeSteps(timeserie, sliding_time, timezone=time.timezone):
    logger.debug('getTimeSteps:')

    timeSteps = []

    logger.debug('   + TimeSerie: %s' % timeserie)

    start_datetime = datetime.utcfromtimestamp(timeserie.timewindow.start)
    stop_datetime = datetime.utcfromtimestamp(timeserie.timewindow.stop)

    if sliding_time:
        stop_datetime = TimeWindow.sliding_time(
            stop_datetime,
            timeserie.period,
            timezone)

    date = stop_datetime
    start_delta = timeserie.period.get_delta(start_datetime)
    start_datetime_minus_delta = start_datetime - start_delta

    date_delta = timeserie.period.get_delta(date)

    while date > start_datetime_minus_delta:
        ts = calendar.timegm(date.timetuple())
        timeSteps.append(ts)
        date_delta = timeserie.period.get_delta(date, date_delta)
        date -= date_delta

    timeSteps.reverse()

    logger.debug('   + timeSteps: %s' % timeSteps)

    return timeSteps


def get_operation(name):
    """
    Get an operation related to an input name.
    """

    if name == TimeSerie.MEAN or not name:
        result = lambda x: sum(x) / float(len(x))
    elif name == TimeSerie.MIN:
        result = lambda x: min(x)
    elif name == TimeSerie.MAX:
        result = lambda x: max(x)
    elif name == TimeSerie.FIRST:
        result = lambda x: x[0]
    elif name == TimeSerie.LAST:
        result = lambda x: x[-1]
    elif name == TimeSerie.DELTA:
        result = lambda x: (max(x) - min(x)) / 2.0

    return result


def timeserie(
        points,
        timewindow,
        timeserie,
        agfn=None,
        timezone=0):

    logger.debug("Aggregate %s points \
        (timewindow: %s, timeserie: %s, \
        operator: %s, timezone: %s)" % (
        len(points),
        timewindow,
        timeserie,
        agfn,
        timezone))

    if not agfn:
        agfn = get_operation(timeserie.operation)

    rpoints = []

    if len(points) == 1:
        return [[timewindow.start, points[0][1]]]

    timeSteps = getTimeSteps(timeserie, timeserie.sliding_time, timezone)

    #initialize variables for loop
    i = 0
    points_to_aggregate = []
    last_point = None

    for index in xrange(1, len(timeSteps)):

        timestamp = timeSteps[index]

        previous_timestamp = timeSteps[index-1]

        logger.debug(
            "   + Interval %s -> %s" %
            (previous_timestamp, timestamp))

        while i < len(points) and points[i][0] < timestamp:

            points_to_aggregate.append(points[i][1])

            i += 1

        if timeserie.operation == TimeSerie.DELTA and last_point:
            points_to_aggregate.insert(0, last_point)

        aggregation_point = get_aggregation_point(
            points_to_aggregate,
            agfn,
            previous_timestamp,
            timeserie.fill)

        rpoints.append(aggregation_point)

        if points_to_aggregate:
            last_point = points_to_aggregate[-1]

        points_to_aggregate = []

    if i < len(points):

        points_to_aggregate = [point[1] for point in points[i:]]

        if timeserie.operation == TimeSerie.DELTA and last_point:
            points_to_aggregate.insert(0, last_point)

        aggregation_point = get_aggregation_point(
            points_to_aggregate,
            agfn,
            timeSteps[-1],
            timeserie.fill)

        rpoints.append(aggregation_point)

    logger.debug(" + Nb points: %s" % len(rpoints))

    return rpoints


def get_aggregation_point(points_to_aggregate, fn, timestamp, fill):
    if points_to_aggregate:

        logger.debug(
            " + %s points to aggregate" % (len(points_to_aggregate)))

        _points_to_aggregate = \
            [point for point in points_to_aggregate if point is None]

        agvalue = round(fn(_points_to_aggregate), 2)

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

        if isinstance(point, list) or isinstance(point, tuple):
            offset = point[0]
            #logger.debug(" + Offset: %s", offset)
            timestamp += offset
            rpoints.append([timestamp, point[1]])
        else:
            timestamp += offset
            rpoints.append([timestamp, point])

        #logger.debug("  %i -> %s" % (i, rpoints[i]))

    return rpoints


def crush_series(series, fn, interval=None):

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
        if start is None or smin < start:
            start = smin
        if stop is None or smax > stop:
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

            nserie.append((ts, last_value))
            ts += interval

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

        i += 1
        ts += interval

    return result


def holtwinters(
        y,
        alpha=Forecast.DEFAULT_ALPHA,
        beta=Forecast.DEFAULT_BETA,
        gamma=Forecast.DEFAULT_GAMMA,
        c=sys.maxint,
        forecast=True):
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

    logger.debug(
        "y = %s, alpha = %s, beta = %s, gamma = %s, c = %s" %
        (y, alpha, beta, gamma, c))

    #Compute initial b and intercept using the first two complete c periods.
    ylen = len(y)

    c = min(c, ylen >> 1)

    fc = float(c)

    ybar2 = sum([y[i] for i in range(c, 2 * c)]) / fc
    ybar1 = sum([y[i] for i in range(c)]) / fc
    b0 = (ybar2 - ybar1) / fc
    logger.debug("b0 = %s" % b0)

    #Compute for the level estimate a0 using b0 above.
    tbar = ((c * (c + 1)) >> 1) / fc
    logger.debug("tbar = %s" % tbar)
    a0 = ybar1 - b0 * tbar
    logger.debug("a0 = %s" % a0)

    #Compute for initial indices
    I = [y[i] / (a0 + (i + 1) * b0) for i in range(0, ylen)]
    logger.debug("Initial indices = %s" % I)

    S = [0] * (ylen + c)
    for i in range(c):
        S[i] = (I[i] + I[i + c]) / 2.0

    #Normalize so S[i] for i in [0, c)  will add to c.
    tS = c / sum([S[i] for i in xrange(c)])

    for i in xrange(c):
        S[i] *= tS
        logger.debug("S[%s]=%s" % (i, S[i]))

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
        logger.debug(
            "i=%s, y=%s, S=%s, Atm1=%s, Btm1=%s, \
            At=%s, Bt=%s, S[i+c]=%s, F=%s" %
            (i + 1, y[i], S[i], Atm1, Btm1, At, Bt, S[i+c], F[i]))

    if forecast:
        holtwinters_forecast(y, c, At, Bt, F, S)

    return c, At, Bt, F


def holtwinters_forecast(y, c, At, Bt, F, S):
    ylen = len(y)
    #Forecast for next c periods:
    for m in xrange(c):
        F[ylen + m] = (At + Bt * (m + 1)) * S[ylen + m]
        logger.debug("forecast: %s" % F[ylen + m])

    logger.debug("F = %s" % F)

    return F


def forecast_best_effort(
        y,
        forecast_parameters=Forecast.PARAMETERS,
        c=sys.maxint,
        calculate_forecast=True):
    """
    Identify best category for forecasting input y list.
    Returns count of forecasting points, At and Bt params and holtwinter list.
    This list is filled if calculate_forecast is True.
    """

    result = None

    for forecast_parameter in forecast_parameters:
        c, At, Bt, F = holtwinters(
            y,
            forecast_parameter[Forecast.ALPHA],
            forecast_parameter[Forecast.BETA],
            forecast_parameter[Forecast.GAMMA], c)
        delta = sum(map(lambda x: abs(x[0] - x[1]), zip(y, F)))

        if result is None or result['delta'] > delta:
            result = forecast_parameter
        else:
            result['delta'] = delta
    if calculate_forecast:
        holtwinters_forecast(y, c, At, Bt, F)

    return result, c, At, Bt, F


def forecast(points, timewindow, forecast):
    """
    Get forecasted points from points and forecast properties.
    """

    logger.debug('forecast: points: %s, forecast: %s' % (points, forecast))

    noneindexes = \
        [index for index, point in enumerate(points) if point[1] is None]

    logger.debug('noneindexes: %s' % noneindexes)

    # remove None values
    y = [point[1] for point in points if point[1] is not None]

    # calculate forecasted points
    if forecast.parameters is None:  # best effort
        forecast_parameters, c, At, Bt, F = forecast_best_effort(
            y,
            Forecast.FORECAST_PARAMETERS,
            c)
        forecast.parameters = forecast_parameters

    else:
        c, At, Bt, F = holtwinters(
            y,
            forecast.parameters.alpha,
            forecast.parameters.beta,
            forecast.parameters.gamma,
            forecast.max_points)

    # add None in F
    def insertnonevalues(F, noneindexes, index=0):
        noneindexeslen = len(noneindexes)
        for _index in xrange(0, noneindexeslen):
            nonindex = noneindexes[_index]
            F.insert(nonindex + index, None)

    insertnonevalues(F, noneindexes)
    insertnonevalues(F, noneindexes, len(y))

    result = [[z[0][0], z[1]] for z in zip(points, F[:len(points)])]

    date = datetime.fromtimestamp(points[-1][0])

    logger.debug('last_point: %s, date: %s' % (points[-1], date))

    for index in xrange(len(points), len(F)):
        date = TimeWindow.get_next_date(
            date,
            timewindow,
            forecast.timeserie.period)
        timestamp = time.mktime(date.timetuple())
        point = [timestamp, F[index]]
        result.append(point)

    logger.debug('points: %s' % points)

    logger.debug('result: %s' % result)

    logger.debug(
        'len(points): %s, len(y): %s, len(F): %s, len(result): %s' %
        (len(points), len(y), len(F), len(result)))

    return result
