#!/usr/bin/python

# Commentary: parse_file will parse a table file and return a list of
# lists of strings for you do do whatever you want with. See Line
# class documentation for more info.

# For future versions:
#   make separators escapable
#   add comment support
#   support for optional columns


from itertools import takewhile, dropwhile
from sys import argv

class Line(object):
    """Just a line aware of it's header, it is able to merge
    """

    def __init__(self, string, head, separator, line = 0):
        self._string = string
        self._head = head
        self._separator = separator

        self._row = string.split(separator)

        self._line = line
        if not separator in string:
            self._row = ['']*len(head)
            return

        if len(self._row) > len(head):
            self._sanitize()
        if len(self._row) < len(head):
            raise Exception("Too few cells on line %d (expected %d, got %d)" % (self._line, len(head), len(self._row)))

        # Spaces are important for spacing
        self._row = map(self.clean_spaces, self._row)

    def _sanitize(self):
        """Try given the separator-based split self._rows to merge to
        get the same number of cells as head based on the cell size"""
        ri = hi = 0
        while ri < len(self._row) - 1:
            if len(self._row) <= len(self._head):
                break

            # While merging cells helps preserve the cell size
            while len(self._row[ri]) < len(self._head[hi]) and abs(len(self._row[ri]) + len(self._row[ri+1]) - len(self._head[hi])) < abs(len(self._row[ri]) - len(self._head[hi])):
                self._row[ri] += self._separator + self._row[ri+1]
                del self._row[ri+1]

            ri+=1
            hi+=1

    def clean_spaces(self, s):
        """Remove spaces from string in the front and back"""
        return s.strip().rstrip()

    def merge(self, line_list):
        """Merge the list of lines with this line"""
        for l in line_list:
            if len(l) != len(self._row):
                raise Exception("Unmatched number fo cells while merging lines.")

            def smart_concat(x, y):
                if not x:
                    return y
                if not y:
                    return x
                return x+"\n"+y

            self._row = map(smart_concat, self._row, l._row)

    def empty_line(self):
        """All cells are empty. most probably a separator or an empty
        line or later maybe a comment"""
        for i in self._row:
            if i != "":
                return False
        return True

    def standalone(self):
        """A standalone row is a row that is not the continuation of it's above"""
        return bool(self._row[0])

    def __len__(self):
        return len(self._row)

    def __repr__(self):
        return str(self._row)

def parse_file(filename, sep):
    """Returns a list of lists with the cells of a table separated by
    separator. The header line is separated from the rest with an
    empty_line. Lines that are not standalone are merged with the
    previous line.  See Line class for more info on parameters."""
    f = open(filename, 'r')
    lines = f.readlines()

    head = lines[0].split(sep)
    rrows = [Line(s[1], head, sep, s[0]) for s in enumerate(lines)]

    # Create header line in head_rows[0]
    head_rows = [i for i in takewhile(lambda x:not x.empty_line(), rrows)]
    head_rows[0].merge(head_rows[1:])

    rows = [head_rows[0]]
    leader = None
    for i in dropwhile(lambda x: not x.standalone(), rrows[len(head_rows):]):
        if not i.standalone():
            leader.merge([i])
        else:
            rows+=[leader]
            leader = i

    return rows
if __name__ == "__main__":
    rows = parse_file(argv[1], '|')
    print rows