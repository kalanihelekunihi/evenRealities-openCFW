#!/usr/bin/env python3
"""Native legacy advertising config and LE parameter command oracle."""
from pathlib import Path
import hashlib
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE, RETURN, CONTROL, HANDLER, LEG, COMMAND, ADDRESS = (
    0x438000, 0x900001, 0x20073394, 0x20073b78, 0x20074fb3, 0x20075000, 0x20076000)
PAYLOAD = PACKAGE.read_bytes()[32:]


def machine():
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(BASE, (len(PAYLOAD) + 4095) & ~4095)
    cpu.mem_write(BASE, PAYLOAD)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x900000, 4096)
    cpu.reg_write(UC_ARM_REG_SP, 0x2007f000)
    cpu.reg_write(UC_ARM_REG_LR, RETURN)
    cpu.mem_write(ADDRESS, b"\x11\x22\x33\x44\x55\x66")
    return cpu


def finish(cpu, address, hook):
    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(address | 1, RETURN, count=2000)
    assert cpu.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1)


def lower_case(own_type, privacy, peer_pointer):
    cpu = machine()
    cpu.mem_write(CONTROL + 0x10, b"\x40\x06")
    cpu.mem_write(CONTROL + 0x14, b"\x80\x07")
    cpu.mem_write(CONTROL + 0x1a, b"\x05")
    cpu.mem_write(HANDLER + 0x0e, bytes([own_type]))
    cpu.mem_write(HANDLER + 0x11, b"\x06")
    cpu.mem_write(HANDLER + 0x16, bytes([privacy]))
    cpu.reg_write(UC_ARM_REG_R0, 4)
    cpu.reg_write(UC_ARM_REG_R1, 1)
    cpu.reg_write(UC_ARM_REG_R2, peer_pointer)
    observed = []

    def hook(uc, pc, _size, _user):
        if pc == RETURN & ~1:
            uc.emu_stop()
        elif pc == 0x52b420:
            sp = uc.reg_read(UC_ARM_REG_SP)
            extra = struct.unpack("<4I", bytes(uc.mem_read(sp, 16)))
            observed.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1),
                             uc.reg_read(UC_ARM_REG_R2), uc.reg_read(UC_ARM_REG_R3), *extra))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    finish(cpu, 0x4b9a80, hook)
    expected_own = own_type + 2 if privacy and own_type <= 1 else own_type
    assert observed == [(0x640, 0x780, 4, expected_own, 1, peer_pointer, 5, 6)], (own_type, privacy, observed)
    assert cpu.mem_read(LEG, 1) == b"\x04"


def hci_case(pointer, allocated):
    cpu = machine()
    cpu.mem_write(COMMAND, bytes([0xa5]) * 40)
    sp = cpu.reg_read(UC_ARM_REG_SP)
    cpu.mem_write(sp, struct.pack("<4I", 1, pointer, 5, 6))
    for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                          (0x640, 0x780, 4, 2)):
        cpu.reg_write(reg, value)
    allocs, sends = [], []

    def hook(uc, pc, _size, _user):
        if pc == RETURN & ~1:
            uc.emu_stop()
        elif pc == 0x52ae38:
            allocs.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
            uc.reg_write(UC_ARM_REG_R0, COMMAND if allocated else 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc == 0x439be4:
            dest, src, size = (uc.reg_read(reg) for reg in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            uc.mem_write(dest, bytes(uc.mem_read(src, size)))
            uc.reg_write(UC_ARM_REG_R0, dest)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc == 0x43c0e4:
            dest, size, value = (uc.reg_read(reg) for reg in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            uc.mem_write(dest, bytes([value & 0xff]) * size)
            uc.reg_write(UC_ARM_REG_R0, dest)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc == 0x52ae5e:
            assert uc.reg_read(UC_ARM_REG_R0) == COMMAND
            sends.append(bytes(uc.mem_read(COMMAND + 3, 15)))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    finish(cpu, 0x52b420, hook)
    expected = b"\x40\x06\x80\x07\x04\x02\x01" + (
        b"\x11\x22\x33\x44\x55\x66" if pointer else bytes(6)) + b"\x05\x06"
    assert allocs == [(0x2006, 15)] and sends == ([expected] if allocated else []), (pointer, allocated, allocs, sends)


def main():
    assert hashlib.sha256(PAYLOAD).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    cases = 0
    for own_type in (0, 1, 2, 3):
        for privacy in (0, 1):
            for pointer in (0, ADDRESS):
                lower_case(own_type, privacy, pointer)
                cases += 1
    for pointer in (0, ADDRESS):
        for allocated in (False, True):
            hci_case(pointer, allocated)
            cases += 1
    print(json.dumps({"status": "PASS_NATIVE_DM_ADV_CONFIG", "cases": cases,
                      "lower_cases": 16, "hci_payload_cases": 4}, indent=2))


if __name__ == "__main__":
    main()
