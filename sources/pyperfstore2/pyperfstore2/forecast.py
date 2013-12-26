import sys
import logging
logger = logging.getLogger('utils')

import time

from datetime import datetime

from timeserie import TimeSerie
from threshold import Threshold


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

    def holtwinters(
            y,
            alpha=DEFAULT_ALPHA,
            beta=DEFAULT_BETA,
            gamma=DEFAULT_GAMMA,
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
            Forecast.holtwinters_forecast(y, c, At, Bt, F, S)

        return c, At, Bt, F

    @staticmethod
    def holtwinters_forecast(y, c, At, Bt, F, S):
        ylen = len(y)
        #Forecast for next c periods:
        for m in xrange(c):
            F[ylen + m] = (At + Bt * (m + 1)) * S[ylen + m]
            logger.debug("forecast: %s" % F[ylen + m])

        logger.debug("F = %s" % F)

        return F

    @staticmethod
    def forecast_best_effort(
            y,
            forecast_parameters=PARAMETERS,
            c=sys.maxint,
            calculate_forecast=True):
        """
        Identify best category for forecasting input y list.
        Returns count of forecasting points, At and Bt params and holtwinter list.
        This list is filled if calculate_forecast is True.
        """

        result = None

        for forecast_parameter in forecast_parameters:
            c, At, Bt, F = Forecast.holtwinters(
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
            Forecast.holtwinters_forecast(y, c, At, Bt, F)

        return result, c, At, Bt, F

    def calculate_points(self, points, timewindow, timeserie):
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
        if self.parameters is None:  # best effort
            forecast_parameters, c, At, Bt, F = Forecast.forecast_best_effort(
                y,
                Forecast.FORECAST_PARAMETERS,
                c)
            self.parameters = forecast_parameters

        else:
            c, At, Bt, F = Forecast.holtwinters(
                y,
                self.parameters.alpha,
                self.parameters.beta,
                self.parameters.gamma,
                self.max_points)

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
            date = timewindow.get_next_date(
                date,
                self.timeserie.period)
            timestamp = time.mktime(date.timetuple())
            point = [timestamp, F[index]]
            result.append(point)

        logger.debug('points: %s' % points)

        logger.debug('result: %s' % result)

        logger.debug(
            'len(points): %s, len(y): %s, len(F): %s, len(result): %s' %
            (len(points), len(y), len(F), len(result)))

        return result
