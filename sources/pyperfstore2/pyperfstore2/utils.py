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

import zlib
import time

import msgpack
packer = None
unpacker = None


def datetimeToTimestamp(_date):
    return time.mktime(_date.timetuple())


def get_overlap(a, b):
    return max(-1, min(a[1], b[1]) - max(a[0], b[0]))


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
