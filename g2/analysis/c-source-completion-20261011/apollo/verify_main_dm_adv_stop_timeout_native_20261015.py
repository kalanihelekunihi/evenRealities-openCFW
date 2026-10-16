#!/usr/bin/env python3
"""Bounded logging-disabled native oracle for legacy advertising stop/timeout."""
from pathlib import Path
import hashlib
import json

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x438000
STATE = 0x20073394 + 0x1d
TYPE = 0x20073394 + 0x18
RETURN = 0x900001


def run(address, state, adv_type, location=3):
    payload = PACKAGE.read_bytes()[32:]
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(BASE, (len(payload) + 4095) & ~4095)
    uc.mem_write(BASE, payload)
    uc.mem_map(0x20000000, 0x100000)
    uc.mem_map(0x900000, 4096)
    uc.mem_write(STATE, bytes([state]))
    uc.mem_write(TYPE, bytes([adv_type]))
    uc.mem_write(0x20074005, b"\x02\x03\x04\x34\x12\x55\x66\x77\x88\x99")
    uc.mem_write(0x20074006, bytes([location]))
    uc.reg_write(UC_ARM_REG_R0, 0x20074000)
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, RETURN)
    calls = []

    def hook(cpu, pc, _size, _user):
        if pc == RETURN & ~1:
            cpu.emu_stop()
        elif pc == 0x4c9c50:  # disabled trace probe
            cpu.reg_write(UC_ARM_REG_R0, 0)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif pc in (0x52b3b0, 0x4b9a80, 0x52b3d2, 0x52b554):
            calls.append((pc, cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1), cpu.reg_read(UC_ARM_REG_R2)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(address | 1, RETURN, count=2000)
    assert uc.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1), hex(uc.reg_read(UC_ARM_REG_PC))
    return uc.mem_read(STATE, 1)[0], calls, bytes(uc.mem_read(0x20073394 + 0x20, 2))


def main():
    payload = PACKAGE.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    cases = 0
    for address in (0x4b9e88, 0x4ba0f4, 0x4ba342):
        for state in range(8):
            for adv_type in range(8):
                changed, calls, duration = run(address, state, adv_type)
                if address == 0x4b9e88:
                    expected = state == 0 and adv_type not in (1, 4)
                    target = (3 if expected else state, [(0x52b3b0, 1)] if expected else [], b"\x34\x12" if expected else b"\0\0")
                else:
                    expected = state == 1 and (address == 0x4ba342 or adv_type not in (1, 4))
                    target = (5 if expected else state, [(0x52b3b0, 0)] if expected else [], b"\0\0")
                assert (changed, [(pc, r0) for pc, r0, _r1, _r2 in calls], duration) == target, (hex(address), state, adv_type, changed, calls, duration)
                cases += 1
    for state in range(8):
        for adv_type in range(8):
            changed, calls, _duration = run(0x4b9ac0, state, adv_type)
            expected = state == 0 and adv_type not in (1, 4)
            assert changed == state
            assert calls == ([(0x4b9a80, 2, 3, 0x20074007)] if expected else []), (state, adv_type, calls)
            cases += 1
    for state in range(8):
        for location in (0, 1, 3):
            changed, calls, _duration = run(0x4b9d24, state, 0, location)
            expected = state == 0
            address = 0x52b3d2 if location == 0 else 0x52b554
            assert changed == state
            assert [(pc, r0, r1) for pc, r0, r1, _r2 in calls] == ([(address, 4, 0x20074008)] if expected else []), (state, location, calls)
            cases += 1
    print(json.dumps({"status": "PASS_NATIVE_DM_ADV_ACTIONS", "cases": cases,
                      "trace_mode": "logging-disabled", "native_addresses": ["0x4b9ac0", "0x4b9d24", "0x4b9e88", "0x4ba0f4", "0x4ba342"]}, indent=2))


if __name__ == "__main__":
    main()
