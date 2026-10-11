#!/usr/bin/env python3
"""Compare original and same-entry next-unblock source over delayed-list state."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = Path("/tmp/g2-audio-arm-inventory/130-source_candidate_20261010-next_unblock_alias.o")
TEXT = Path("/tmp/next-unblock-alias.text")
raw = OTA.read_bytes()[32:]
compiled = TEXT.read_bytes()

def run(variant, count, head_value, prior):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    list_address = 0x20006000
    item_address = 0x20006100
    def word(address, value):
        u.mem_write(address, struct.pack("<I", value))
    word(0x20074a24, list_address)
    word(0x20074a50, prior)
    word(list_address, count)
    word(list_address + 12, item_address)
    word(item_address, head_value)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100301)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _cpu, _access, address, size, value, _data:
               writes.append([address, size, value]))
    u.emu_start(0x455877 if variant == "original" else 0x1000a5,
                0x100300, count=100)
    return {"writes": writes,
            "next_unblock": struct.unpack("<I", u.mem_read(0x20074a50, 4))[0],
            "list": bytes(u.mem_read(list_address, 0x110)).hex(),
            "sp": u.reg_read(UC_ARM_REG_SP), "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for count in (0, 1, 3):
    for value in (0, 1, 100, 0xfffffffe, 0xffffffff):
        original = run("original", count, value, 0x12345678)
        alias = run("alias", count, value, 0x12345678)
        assert original == alias, (count, value, original, alias)
        assert original["next_unblock"] == (value if count else 0xffffffff)
        cases.append({"count": count, "head_value": value,
                      "observed_write": original["writes"]})

result = {"matched": len(cases), "total": len(cases), "cases": cases,
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "Original 0x455876 versus Clang Cortex-M55 same-entry source function; coherent synthetic delayed-list header and head item. Compares ordered write, unchanged list, SP/PC. No scheduler tick or task switch."}
Path(__file__).with_name("next-unblock-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} next-unblock original/source cases pass")
