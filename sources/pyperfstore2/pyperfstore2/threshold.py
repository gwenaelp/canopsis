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
