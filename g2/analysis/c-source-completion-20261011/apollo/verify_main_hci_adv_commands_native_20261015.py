#!/usr/bin/env python3
"""Bounded native command-payload oracle for legacy LE advertising HCI calls."""
from pathlib import Path
import hashlib
import json

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x438000
RETURN = 0x900001
COMMAND = 0x20075000
DATA = 0x20076000


def run(address, length, value, allocation):
    payload = PACKAGE.read_bytes()[32:]
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(BASE, (len(payload) + 4095) & ~4095)
    uc.mem_write(BASE, payload)
    uc.mem_map(0x20000000, 0x100000)
    uc.mem_map(0x900000, 4096)
    uc.mem_write(DATA, bytes(range(1, 33)))
    uc.mem_write(COMMAND, bytes([0xa5]) * 40)
    uc.reg_write(UC_ARM_REG_R0, length if address != 0x52b3b0 else value)
    uc.reg_write(UC_ARM_REG_R1, DATA)
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, RETURN)
    allocs, sends = [], []

    def hook(cpu, pc, _size, _user):
        if pc == RETURN & ~1:
            cpu.emu_stop()
        elif pc == 0x52ae38:
            opcode, size = cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1)
            allocs.append((opcode, size))
            cpu.reg_write(UC_ARM_REG_R0, COMMAND if allocation else 0)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif pc == 0x439be4:
            dest, src, size = (cpu.reg_read(register) for register in
                               (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            cpu.mem_write(dest, bytes(cpu.mem_read(src, size)))
            cpu.reg_write(UC_ARM_REG_R0, dest)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif pc == 0x43c0e4:
            dest, size, value_byte = (cpu.reg_read(register) for register in
                                      (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            cpu.mem_write(dest, bytes([value_byte & 0xff]) * size)
            cpu.reg_write(UC_ARM_REG_R0, dest)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif pc == 0x52ae5e:
            assert cpu.reg_read(UC_ARM_REG_R0) == COMMAND
            sends.append(bytes(cpu.mem_read(COMMAND + 3, 32 if address != 0x52b3b0 else 1)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(address | 1, RETURN, count=2000)
    assert uc.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1)
    return allocs, sends


def main():
    payload = PACKAGE.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    cases = 0
    for enable in (0, 1, 0xff):
        for allocated in (False, True):
            allocs, sends = run(0x52b3b0, 0, enable, allocated)
            assert allocs == [(0x200a, 1)] and sends == ([bytes([enable])] if allocated else [])
            cases += 1
    for address, opcode in ((0x52b3d2, 0x2008), (0x52b554, 0x2009)):
        for length in (0, 1, 8, 31):
            for allocated in (False, True):
                allocs, sends = run(address, length, 0, allocated)
                expected = bytes([length]) + bytes(range(1, length + 1)) + bytes(31 - length)
                assert allocs == [(opcode, 32)] and sends == ([expected] if allocated else []), (hex(address), length, allocated, allocs, sends)
                cases += 1
    print(json.dumps({"status": "PASS_NATIVE_HCI_ADV_COMMANDS", "cases": cases,
                      "payload_lengths": [0, 1, 8, 31], "allocation_paths": [False, True]}, indent=2))


if __name__ == "__main__":
    main()
