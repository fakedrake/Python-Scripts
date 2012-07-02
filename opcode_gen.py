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
    def __init__(self, row):
        self._row = row

    def get_name(self):
        return self._row["opcode"]

    def get_inst_type(self):
        """This has to do with arguments"""
        prefix = "INST_TYPE_"
        identifier = ""
        regs = 0

        arguments = self._row["syntax"].split(',')
        # rd,rs,rt,imm,Imm<Bits>

        #TODO specials, unsigned
        if "rs" in arguments:
            regs += 1
        if "rt" in arguments:
            regs += 1

        if "rd" in arguments:
            identifier += "RD"
        for i in range(1,regs+1):
            identifier += "_R"+str(i)
        if "imm" in arguments:
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

if __name__ == "__main__":
    table = parse_file("testtable.txt")
    head = table[0]
    for i in table[1:]:
        print OpcodeStruct(Row(head, i)),','
