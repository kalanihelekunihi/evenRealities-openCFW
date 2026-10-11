#!/usr/bin/env python3
"""Compare original Apollo uxListRemove with same-entry source alias."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = Path("/tmp/g2-audio-arm-inventory/131-source_candidate_20261010-list_remove_alias.o")
TEXT = Path("/tmp/list-alias.text")
raw = OTA.read_bytes()[32:]
compiled = TEXT.read_bytes()
L, S, I, J = 0x20006000, 0x20006008, 0x20006100, 0x20006120

def run(variant, count, target_index, index_at):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    def words(address, *values):
        u.mem_write(address, struct.pack("<" + "I" * len(values), *values))
    items = [I] if count == 1 else [I, J]
    target = items[target_index]
    index = {"target": target, "sentinel": S,
             "other": items[1 - target_index] if count == 2 else S}[index_at]
    words(L, count, index)
    words(S, 0xffffffff, items[0], items[-1])
    for position, item in enumerate(items):
        words(item, 100 + position, items[position + 1] if position + 1 < count else S,
              items[position - 1] if position else S, 0x20007000 + position, L)
    u.reg_write(UC_ARM_REG_R0, target)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100301)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _cpu, _access, address, size, value, _data:
               writes.append([address, size, value]))
    u.emu_start(0x4560e9 if variant == "original" else 0x10001d,
                0x100300, count=100)
    return {"list": bytes(u.mem_read(L, 0x140)).hex(),
            "return": u.reg_read(UC_ARM_REG_R0),
            "writes": writes, "sp": u.reg_read(UC_ARM_REG_SP),
            "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for count, target_index, index_at in ((1, 0, "target"), (1, 0, "sentinel"),
                                       (2, 0, "target"), (2, 0, "other"),
                                       (2, 0, "sentinel"), (2, 1, "target"),
                                       (2, 1, "other"), (2, 1, "sentinel")):
    original = run("original", count, target_index, index_at)
    alias = run("alias", count, target_index, index_at)
    assert original["list"] == alias["list"]
    assert original["return"] == alias["return"] == count - 1
    assert original["sp"] == alias["sp"] == 0x2007e000
    assert original["pc"] == alias["pc"] == 0x100300
    assert original["writes"] == alias["writes"], (count, target_index, index_at, original["writes"], alias["writes"])
    cases.append({"count": count, "target_index": target_index,
                  "index_at": index_at, "writes": original["writes"]})

result = {"matched": len(cases), "total": len(cases), "cases": cases,
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "Original 0x4560e8 versus Clang Cortex-M55 source alias on coherent one/two item lists; ordered writes, complete list fixture, return count, SP/PC. No concurrent list mutation."}
Path(__file__).with_name("list-remove-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} list-remove original/source cases pass")
