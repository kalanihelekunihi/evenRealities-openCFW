#!/usr/bin/env python3
"""Stop stock hciEvtProcessMsg at WsfBufAlloc for LE subevent 34."""
import hashlib
import json
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R8, UC_ARM_REG_SP,
    UC_CPU_ARM_CORTEX_M4,
)

ROOT = Path(__file__).resolve().parents[5]
blob = (ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
blob_hash = hashlib.sha256(blob).hexdigest()
assert blob_hash == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
cpu.mem_map(0x400000, 0x400000)
cpu.mem_write(0x438000, blob)
cpu.mem_map(0x20000000, 0x100000)
event = 0x20081000
cpu.mem_write(event, bytes((0x3e, 1, 34, 0)))
cpu.reg_write(UC_ARM_REG_R0, event)
cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
cpu.reg_write(UC_ARM_REG_LR, 0x600001)
seen = []

def capture(uc, address, size, user_data):
    if address == 0x530446:
        seen.append({"allocator_size": uc.reg_read(UC_ARM_REG_R0),
                     "callback_type": uc.reg_read(UC_ARM_REG_R8),
                     "allocator_pc": hex(uc.reg_read(UC_ARM_REG_PC))})
        uc.emu_stop()

cpu.hook_add(UC_HOOK_CODE, capture)
cpu.emu_start(0x56b391, 0x600000, count=10000)
assert seen == [{"allocator_size": 0, "callback_type": 85,
                 "allocator_pc": "0x530446"}], seen
print(json.dumps({"status": "PASS_NATIVE_HCI_EVENT_85_ALLOCATION",
                  "stock_blob_sha256": blob_hash, "event_bytes": [0x3e, 1, 34, 0],
                  "observation": seen[0],
                  "limit": "Allocator call observed; original table allocation extent and later runtime unproven"}))
