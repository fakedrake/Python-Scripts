#!/usr/bin/python

from  isa_parser import Row, parse_file
import re

# add to opcodes[] in scavenger.h
# add to instr

# inst types
# INST_TYPE_RD_R1_R2           0
# INST_TYPE_RD_R1_IMM          1
# INST_TYPE_RD_R1_UNSIGNED_IMM 2
# INST_TYPE_RD_R1              3
# INST_TYPE_RD_R2              4
# INST_TYPE_RD_IMM             5
# INST_TYPE_R2                 6
# INST_TYPE_R1_R2              7
# INST_TYPE_R1_IMM             8
# INST_TYPE_IMM                9
# INST_TYPE_SPECIAL_R1        10
# INST_TYPE_RD_SPECIAL        11
# INST_TYPE_R1

class OpcodeStruct:
    """This class represents the C struct in binutils vreated in binutils/opcodes/<target-name>-opc.h"""
    def __init__(self, row):
        """The argument here is a dict with the names and values of
        info obtained from tables. Supported names:
        syntax: <comma split argument list [rd | rs | rt | imm | Imm<num>]
        """
        self._row = row
        self._private_args = None

        self.R = re.compile("r[st]")
        self.RD = re.compile("rd")
        self.IMM = re.compile("[iI]mm\d*")

    def get_name(self):
        return self._row["opcode"]

    def _match_arg(self, regex, args = None):
        """Match once and dont match again. Providing args resets self._private_args"""
        if args:
           self._private_args = args

        for i in range(len(self._private_args)):
            if regex.match(self._private_args[i]):
                del self._private_args[i]
                return True
        return False

    def get_inst_type(self):
        """This has to do with arguments"""
        prefix = "INST_TYPE"
        identifier = ""
        regs = 0

        self._private_args = self._row["syntax"].split(',')
        # rd,rs,rt,imm,Imm<Bits>

        #TODO specials, unsigned
        if self._match_arg(self.R):
            regs += 1
        if self._match_arg(self.R):
            regs += 1
        if self._match_arg(self.RD):
            identifier += "_RD"
        for i in range(regs):
            identifier += "_R"+str(i+1)
        if self._match_arg(self.IMM):
            identifier += "_IMM"

        return prefix+identifier

    def get_bitfield(self):
        # MAJOR/MINOR : 6bit, ALL: 32bit
        non_dig = re.compile("\D")

        minor = 0
        major = int(self._row["MAJOR"])
        if not non_dig.search(self._row["MINOR"]):
            minor = int(self._row["MINOR"])

        return major<<26 | minor

    def get_mask(self):
        mask = 0x3f<<(32-6)

        non_dig = re.compile("\D")
        if not non_dig.search(self._row["MINOR"]):
            mask |= 0x3f

        return mask

    def get_instr_type(self):
        """This has to do with the nature of the intruction"""
        if not "instruction type" in self._row.keys():
            return "0"

        return self._row["instruction type"]

    def __repr__(self):
        init = '{"%(name)s",   %(inst_type)s,  INST_NO_OFFSET, NO_DELAY_SLOT, IMMVAL_MASK_NON_SPECIAL, %(bitfield)s, %(mask)s, %(name)s, %(instr_type)s }' % dict(name = self.get_name(), inst_type = self.get_inst_type(), bitfield = hex(self.get_bitfield()), mask = hex(self.get_mask()), instr_type = self.get_instr_type())
        return init

def opcodeStructFactory(filename):
    """Create a list of opcode struct as presented in the table in filename (deliminer = '|')"""
    table = parse_file(filename)
    head = table[0]
    return [OpcodeStruct(Row(head, i)) for i in table[1:]]



if __name__ == "__main__":
    from sys import argv
    print opcodeStructFactory(argv[1])
