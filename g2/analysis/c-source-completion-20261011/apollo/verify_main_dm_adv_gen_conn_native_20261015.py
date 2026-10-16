#!/usr/bin/env python3
"""Native record oracle for synthetic enhanced advertising connection completion."""
from pathlib import Path
import hashlib
import json

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = (ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
BASE, RETURN, CONTROL = 0x438000, 0x900001, 0x20073394


def run(handle, status):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(BASE, (len(PAYLOAD) + 4095) & ~4095)
    cpu.mem_write(BASE, PAYLOAD)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x900000, 4096)
    cpu.mem_write(CONTROL + 0x25, bytes(range(0x11, 0x1d)))
    cpu.mem_write(CONTROL + 0x31, b"\x01\x02")
    cpu.reg_write(UC_ARM_REG_R0, handle)
    cpu.reg_write(UC_ARM_REG_R1, status)
    cpu.reg_write(UC_ARM_REG_SP, 0x2007f000)
    cpu.reg_write(UC_ARM_REG_LR, RETURN)
    records = []

    def hook(uc, pc, _size, _user):
        if pc == RETURN & ~1:
            uc.emu_stop()
        elif pc == 0x43c0e4:
            dest, size, value = (uc.reg_read(reg) for reg in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            uc.mem_write(dest, bytes([value & 0xff]) * size)
            uc.reg_write(UC_ARM_REG_R0, dest)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc == 0x439be4:
            dest, src, size = (uc.reg_read(reg) for reg in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            uc.mem_write(dest, bytes(uc.mem_read(src, size)))
            uc.reg_write(UC_ARM_REG_R0, dest)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc == 0x4d29c2:
            records.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0), 36)))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(0x4b310b, RETURN, count=2000)
    assert cpu.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1)
    return records


def main():
    assert hashlib.sha256(PAYLOAD).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    cases = 0
    for handle in (0, 1):
        for status in (0, 1, 0x3c, 0xff):
            expected = bytearray(36)
            expected[2] = 2
            expected[3] = expected[4] = status
            expected[8] = 1
            expected[9] = handle + 1
            expected[10:16] = bytes(range(0x11 + 6 * handle, 0x17 + 6 * handle))
            assert run(handle, status) == [bytes(expected)], (handle, status)
            cases += 1
    print(json.dumps({"status": "PASS_NATIVE_DM_ADV_GEN_CONN", "cases": cases,
                      "record_bytes": 36}, indent=2))


if __name__ == "__main__":
    main()
