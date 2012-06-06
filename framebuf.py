#!/usr/bin/python2.7

import struct

XRES = 800
YRES = 480

class Counter:
    """Counts up to a maximum in a given amount of steps
    """

    def __init__(self, max, steps):
        """Set the target value and the steps required to reach there

        Arguments:
        - `max` :
        - `steps`:
        """
        self._max = max
        self._steps = steps
        self._current = 0

    def next(self):
        """Next number
        """
        ret = float(self._current)/float(self._steps)*self._max
        self._current += 1
        self._current %= self._steps
        return ret

if __name__ == "__main__":
    of = file("fb.rgba","wb")

    r = Counter(255, XRES)
    g = Counter(255, YRES)

    for y in range(YRES):
        _g = g.next()
        for x in range(XRES):
            _r = r.next()
            of.write(struct.pack("BBBB", _r, _g, 0, 0x80))
