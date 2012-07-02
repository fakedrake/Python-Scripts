#!/usr/bin/python

import shutil
import opcode_gen
import re

# This adds C code to a specific file but it might aswell edit any
# file. You can use this class to edit verilog files aswell. See
# example code at the end.

class CFile:
    """
    Will write whatever you feed push_line(s) in the space between the
    deliminer string, formated with begin_id or end_id as begin_or_end
    and with generate_tag as tag.

    Also keeps backup according to argument backup_format (only format
    argument is the string filename).

    Note1: The first occrance of deliminers will be used ONLY. Use
    different tags to edit different parts of the file separately.

    Note2: The lines containing deliminers are left untouched. Keeping
    them completely separate is suggested.

    Note3: any changes commited to the file between tha beginning and
    end of a CFile's lifetime will be overwritten
    """
    def __init__(self, filename, generate_tag, deliminer_string = "/* %(begin_or_end)s generated code: %(tag)s */", begin_id = "Begin", end_id = "End", backup_format = "%s~"):
        """
        filename:     The filename to edit

        generate_tag: Each automatically editable region has a unique
                      tag that characterizes the control domain of
                      Cfile

        deliminer_string: This is a formatable string with parameters
                          begin_or_end to distinguish between start
                          and end deliminer and tag to distingush
                          between the regions of control of different
                          CFile objects

        begin_id: Substituted in deliminer_string to retrieve the
                  beginning of the control region

        end_id: Substituted in deliminer_string to retrieve the
                end of the control region

        backup_format: the format of the backup file that is
                       automatically kept. Set to None for no backup.
        """
        if backup_format:
            shutil.copy(filename, backup_format % filename)
        else:
            backup_format = "%s"

        self.backup_file = open(backup_format % filename, "r")

        self.top_list = []
        self.mid_list = []
        self.bottom_list = []

        self.pattern = {'begin': deliminer_string % dict(begin_or_end = begin_id, tag = generate_tag), 'end' : deliminer_string % dict(begin_or_end = end_id, tag = generate_tag)}

        checkpoints = iter(['begin', 'end'])
        looking_for = next(checkpoints, None)
        for i in self.backup_file:
            if looking_for == 'begin':
                self.top_list += [i]

            if looking_for and self.pattern[looking_for] in i:
                looking_for = next(checkpoints, None)

            if looking_for == None:
                self.bottom_list += [i]

        self.backup_file.close()

        if looking_for:
            raise Exception("Failed to find "+looking_for+" tag: "+self.pattern[looking_for])

        self._filename = filename

    def push_line(self, string):
        """Push line to be written to the file. Nothing is written
        until flush is called. Lines should contain newline
        characters."""
        self.mid_list += [string]

    def push_lines(self, lines):
        """Same as above only accepts a list of lines."""
        self.mid_list += lines

    def flush(self):
        """Flushong also closes the file"""
        self.file = open(self._filename, 'w')
        self.file.writelines( [str(i) for i in self.top_list + self.mid_list + self.bottom_list] )
        self.file.close()

if __name__ == "__main__":
    from sys import argv

    # Assuming scavenger-opc.h is in the current directory.
    # The only thing that would change for a verilog file would be the __init__ parameters:
    # f = Cfile('file.v', 'tag_name', '// some comment that contains %(begin_or_end)s and %(tag)s')

    f = CFile('scavenger-opc.h', 'OpcodeStruct')
    f.push_lines([str(i)+",\n" for i in opcode_gen.opcodeStructFactory('testtable.txt')])
    f.flush()
