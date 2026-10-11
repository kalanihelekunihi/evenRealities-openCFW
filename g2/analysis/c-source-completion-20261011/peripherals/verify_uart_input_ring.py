"""Bounded stock/source-model comparison for 0x46d8c4 on valid RAM rings.

Unicorn lacks ARMv8-M LDA/STL, so the two exact instructions in the
authenticated core are interpreted as ordinary word load/store. Their
single-threaded values are unchanged; memory-order behavior is untested.
"""
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R9,
                               UC_ARM_REG_SP)
from unicorn.unicorn_const import UC_HOOK_CODE

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
START, RETURN = 0x46D8C5, 0x600000
DESC, SOURCE, BUFFER = 0x20001000, 0x20002000, 0x20003000


def original(read_index, write_index, length, capacity=16):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_write(0x438000, BLOB)
    uc.mem_map(0x20000000, 0x100000)
    uc.mem_write(DESC, struct.pack("<5I", BUFFER, capacity, read_index,
                                   write_index, 0))
    uc.mem_write(SOURCE, b"abcdefghijklm")
    uc.mem_write(BUFFER, b"ABCDEFGHIJKLMNOP"[:capacity])
    uc.reg_write(UC_ARM_REG_SP, 0x200FF000)
    uc.reg_write(UC_ARM_REG_LR, RETURN | 1)
    uc.reg_write(UC_ARM_REG_R0, DESC)
    uc.reg_write(UC_ARM_REG_R1, SOURCE)
    uc.reg_write(UC_ARM_REG_R2, length)

    def hook(machine, address, _size, _):
        if address == RETURN:
            machine.emu_stop()
        elif address == 0x46D932:  # LDA SB,[R0]
            value = struct.unpack("<I", machine.mem_read(machine.reg_read(UC_ARM_REG_R0), 4))[0]
            machine.reg_write(UC_ARM_REG_R9, value)
            machine.reg_write(UC_ARM_REG_PC, address + 5)
        elif address == 0x46D986:  # STL SB,[R0]
            machine.mem_write(machine.reg_read(UC_ARM_REG_R0),
                              struct.pack("<I", machine.reg_read(UC_ARM_REG_R9)))
            machine.reg_write(UC_ARM_REG_PC, address + 5)

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(START, RETURN, count=10000)
    return (uc.reg_read(UC_ARM_REG_R0),
            struct.unpack("<5I", uc.mem_read(DESC, 20))[3],
            bytes(uc.mem_read(BUFFER, capacity)))


def source_model(read_index, write_index, length, capacity=16):
    data = bytearray(b"ABCDEFGHIJKLMNOP"[:capacity])
    if length == 0:
        return 0, write_index, bytes(data)
    free = (read_index - write_index - 1 if write_index < read_index
            else capacity - write_index + read_index - 1)
    if free == 0:
        return 0, write_index, bytes(data)
    length = min(length, free)
    source = b"abcdefghijklm"
    first = min(length, capacity - write_index)
    data[write_index:write_index + first] = source[:first]
    remainder = length - first
    if remainder:
        data[:remainder] = source[first:first + remainder]
    end = (write_index + first if remainder == 0 else remainder)
    if end >= capacity:
        end = 0
    return length, end, bytes(data)


cases = [(0, 0, 5), (12, 14, 5), (2, 10, 10), (5, 4, 5),
         (0, 0, 0), (8, 15, 1), (15, 0, 13)]
for case in cases:
    stock, source = original(*case), source_model(*case)
    assert stock == source, (case, stock, source)
print(f"PASS {len(cases)}/{len(cases)} native/source-model ring transitions")
