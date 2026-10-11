#!/usr/bin/env python3
"""Compare Apollo vListInsert and the Cortex-M55 same-entry alias."""
import hashlib
import json
from pathlib import Path
import struct

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = Path("/tmp/g2-audio-arm-inventory/132-source_candidate_20261010-sorted_insert_alias.o")
TEXT = Path("/tmp/g2-audio-sorted-new.text")
raw = OTA.read_bytes()[32:]
compiled = TEXT.read_bytes()
L, S, I = 0x20006000, 0x20006008, 0x20006100

def run(variant, prior, inserted, index_at):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(raw) + 4095) & ~4095)
    u.mem_write(0x438000, raw)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    def words(address, *values):
        u.mem_write(address, struct.pack("<" + "I" * len(values), *values))
    items = [0x20006120 + 0x20 * j for j in range(len(prior))]
    index = S if not items or index_at == "sentinel" else items[-1]
    words(L, len(prior), index)
    words(S, 0xffffffff, items[0] if items else S, items[-1] if items else S)
    for j, item in enumerate(items):
        words(item, prior[j], items[j + 1] if j + 1 < len(items) else S,
              items[j - 1] if j else S, 0x20007000 + j, L)
    words(I, inserted, 0, 0, 0x20007080, 0)
    u.reg_write(UC_ARM_REG_R0, L)
    u.reg_write(UC_ARM_REG_R1, I)
    u.reg_write(UC_ARM_REG_SP, 0x2007e000)
    u.reg_write(UC_ARM_REG_LR, 0x100301)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _cpu, _access, address, size, value, _data:
               writes.append([address, size, value]) if address < 0x2007d000 else None)
    u.emu_start(0x4560b3 if variant == "original" else 0x100001,
                0x100300, count=100)
    return {"list": bytes(u.mem_read(L, 0x160)).hex(),
            "writes": writes, "sp": u.reg_read(UC_ARM_REG_SP),
            "pc": u.reg_read(UC_ARM_REG_PC)}

cases = []
for prior, inserted, index_at in (([], 0, "sentinel"), ([], 0xffffffff, "sentinel"),
                                  ([1], 0, "last"), ([1], 1, "sentinel"),
                                  ([1], 2, "last"), ([1], 0xffffffff, "last"),
                                  ([0, 1, 1, 100], 1, "last"),
                                  ([0, 1, 1, 100], 0xffffffff, "sentinel")):
    original = run("original", prior, inserted, index_at)
    alias = run("alias", prior, inserted, index_at)
    assert original == alias, (prior, inserted, index_at, original, alias)
    assert original["sp"] == 0x2007e000 and original["pc"] == 0x100300
    cases.append({"prior_values": prior, "inserted": inserted,
                  "index_at": index_at, "writes": original["writes"]})

result = {"matched": len(cases), "total": len(cases), "cases": cases,
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "scope": "Original 0x4560b2 versus Clang Cortex-M55 same-entry source alias on coherent sorted lists; ordered writes, complete list fixture, SP/PC. No concurrent mutation."}
Path(__file__).with_name("sorted-insert-alias-execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} sorted-insert original/source cases pass")
