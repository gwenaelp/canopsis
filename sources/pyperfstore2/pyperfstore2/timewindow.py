import logging
logger = logging.getLogger('utils')

import time

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

    def sliding_time(self, utcdate, timezone=0):
        """
        Calculate roudtime relative to an UTC date, a period time/type
        and a timezone.
        """
        result = utcdate

        dt = timedelta(seconds=timezone)
        result -= dt

        # assume result does not contain seconds and microseconds in this case
        result = result.replace(second=0, microsecond=0)

        if self.unit == Period.SECOND:
            seconds = (result.second * 60 / self.value) * self.value / 60
            result = result.replace(second=seconds)

        elif self.unit == Period.MINUTE:
            minutes = (result.minute * 60 / self.value) * self.value / 60
            result = result.replace(minute=minutes)

        else:
            result = result.replace(minute=0)

            index_unit = Period.UNITS.index(self.unit)

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


class TimeWindow(object):
    """
    Time window management with exclusion intervals.
    Contains a start/stop dates and an array of exclusion intervals
    (couple of START, STOP timestamp).
    """

    def __init__(self, start, stop=time.time(), exclusion_intervals=[], timezone=0):
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

    def get_next_date(self, date, period, delta=None):
        """
        Get next date of input date with timewindow parameters,
        period and optionaly a previous calculated delta.
        """

        delta = period.get_delta(date, delta)
        # check if next date is in exclusion dates of the input timewindow
        result = date + delta
        return result

    def get_previous_date(self, date, delta=None):
        """
        Get previous date of input date with timewindow parameters,
        period and optionaly a previous calculated delta.
        """

        delta = self.period.get_delta(date, delta)
        # check if next date is in exclusion dates of the input timewindow
        result = date - delta
        return result

    @staticmethod
    def get_datetime(timestamp, timezone=0):
        dt = timedelta(seconds=timezone)
        result = datetime.utcfromtimestamp(timestamp) - dt
        return result
