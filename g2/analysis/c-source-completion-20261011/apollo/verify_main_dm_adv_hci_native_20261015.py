#!/usr/bin/env python3
"""Logging-disabled native oracle for legacy advertising HCI events."""
from pathlib import Path
import hashlib
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE, RETURN, CALLBACK = 0x438000, 0x900001, 0x900101
CONTROL, HANDLER, LEG, EVENT = 0x20073394, 0x20073b78, 0x20074fb3, 0x20076000
PAYLOAD = PACKAGE.read_bytes()[32:]


def run(state, status, leg_type, duration, event_code):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(BASE, (len(PAYLOAD) + 4095) & ~4095)
    cpu.mem_write(BASE, PAYLOAD)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x900000, 4096)
    cpu.mem_write(CONTROL + 0x18, b"\x77")
    cpu.mem_write(CONTROL + 0x1d, bytes([state]))
    cpu.mem_write(CONTROL + 0x20, struct.pack("<H", duration))
    cpu.mem_write(LEG, bytes([leg_type]))
    cpu.mem_write(HANDLER + 8, struct.pack("<I", CALLBACK))
    cpu.mem_write(EVENT, bytes([0, 0, event_code, status]) + bytes(36))
    cpu.reg_write(UC_ARM_REG_R0, EVENT)
    cpu.reg_write(UC_ARM_REG_SP, 0x2007f000)
    cpu.reg_write(UC_ARM_REG_LR, RETURN)
    calls = []

    def hook(uc, pc, _size, _user):
        if pc == RETURN & ~1:
            uc.emu_stop()
        elif pc == 0x4c9c50:
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif pc in (0x52a4c4, 0x52a4d2, 0x4b2ea6, 0x4b310a, CALLBACK & ~1):
            calls.append((pc, uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1),
                          uc.reg_read(UC_ARM_REG_R2), uc.reg_read(UC_ARM_REG_R3)))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(0x4ba4b1, RETURN, count=2000)
    assert cpu.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1)
    return (cpu.mem_read(CONTROL + 0x18, 1)[0],
            cpu.mem_read(CONTROL + 0x1d, 1)[0],
            cpu.mem_read(CONTROL + 0x0a, 1)[0],
            cpu.mem_read(EVENT + 2, 1)[0], calls)


def main():
    assert hashlib.sha256(PAYLOAD).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    cases = 0
    for state in range(8):
        for status in (0, 1):
            for leg_type in (0, 4):
                for duration in (0, 10):
                    for event_code in (0x35, 0x34):
                        result = run(state, status, leg_type, duration, event_code)
                        adv_type, final_state, timer_event, final_event, calls = result
                        expected_type, expected_state, expected_timer, expected_event = 0x77, state, 0, event_code
                        expected_calls = []
                        if event_code == 0x35 and state in (2, 3):
                            if status == 0:
                                if state == 3 and duration:
                                    expected_timer = 7
                                    expected_calls.append((0x52a4c4, CONTROL, duration))
                                expected_calls.append((0x4b2ea6, 12, 0x21))
                                expected_type, expected_state = leg_type, 1
                                if state == 3 and leg_type != 4:
                                    expected_event = 0x21
                                    expected_calls.append((CALLBACK & ~1, EVENT, None))
                            else:
                                expected_state = 0
                        elif event_code == 0x35 and state in (4, 5):
                            if status == 0:
                                if state == 5:
                                    expected_calls.append((0x52a4d2, CONTROL, None))
                                expected_calls.append((0x4b2ea6, 13, 0x22))
                                expected_type, expected_state = 0xff, 0
                                if state == 5:
                                    if leg_type == 4:
                                        expected_calls.append((0x4b310a, 0, 0x3c))
                                    else:
                                        expected_event = 0x22
                                        expected_calls.append((CALLBACK & ~1, EVENT, None))
                            else:
                                expected_state = 1
                        compact = [(pc, r0, r1 if pc in (0x52a4c4, 0x4b2ea6, 0x4b310a) else None)
                                   for pc, r0, r1, _r2, _r3 in calls]
                        assert (adv_type, final_state, timer_event, final_event, compact) == (
                            expected_type, expected_state, expected_timer, expected_event, expected_calls), (state, status, leg_type, duration, event_code, result, expected_calls)
                        cases += 1
    print(json.dumps({"status": "PASS_NATIVE_DM_ADV_HCI", "cases": cases,
                      "trace_mode": "logging-disabled"}, indent=2))


if __name__ == "__main__":
    main()
