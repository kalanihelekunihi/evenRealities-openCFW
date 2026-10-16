#!/usr/bin/env python3
"""Native selected connection-interface callback forwarding oracle."""
from pathlib import Path
import hashlib
import json
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
PAYLOAD = (ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
BASE, RETURN, CALLBACK = 0x438000, 0x900001, 0x900101
CONFIG, TABLE, EVENT = 0x20000694, 0x20074000, 0x20076000


def run(seed):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(BASE, (len(PAYLOAD) + 4095) & ~4095)
    cpu.mem_write(BASE, PAYLOAD)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x900000, 4096)
    cpu.mem_write(CONFIG + 0x0c, struct.pack("<I", TABLE))
    cpu.mem_write(TABLE + 4, struct.pack("<I", CALLBACK))
    record = bytes((seed + i) & 0xff for i in range(36))
    cpu.mem_write(EVENT, record)
    cpu.reg_write(UC_ARM_REG_R0, EVENT)
    cpu.reg_write(UC_ARM_REG_SP, 0x2007f000)
    cpu.reg_write(UC_ARM_REG_LR, RETURN)
    observed = []

    def hook(uc, pc, _size, _user):
        if pc == RETURN & ~1:
            uc.emu_stop()
        elif pc == CALLBACK & ~1:
            observed.append((uc.reg_read(UC_ARM_REG_R0), bytes(uc.mem_read(EVENT, 36))))
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(0x4d29c3, RETURN, count=100)
    assert cpu.reg_read(UC_ARM_REG_PC) in (RETURN, RETURN & ~1)
    assert observed == [(EVENT, record)]


def main():
    assert hashlib.sha256(PAYLOAD).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    for seed in range(16):
        run(seed)
    print(json.dumps({"status": "PASS_NATIVE_DM_DEV_PASS_HCI_CONN", "cases": 16,
                      "config_slot": "0x200006a0", "interface_callback_slot": 1}, indent=2))


if __name__ == "__main__":
    main()
