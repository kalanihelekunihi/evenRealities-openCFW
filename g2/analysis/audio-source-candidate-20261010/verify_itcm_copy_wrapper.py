#!/usr/bin/env python3
"""Compare original 0x48086a plus authenticated ITCM 0x48 with source copy."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_MEM_WRITE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R7,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M33)

ROOT = Path(__file__).resolve().parents[3]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "g2/components/audio/source_candidate_20261010/itcm_copy_provider.c"
OBJECT = Path("/tmp/g2-audio-arm-inventory/123-source_candidate_20261010-itcm_copy_provider.o")
DECODER = ROOT / "g2/analysis/audio-platform-callbacks-closure-2026-10-08/itcm_record.py"
spec = importlib.util.spec_from_file_location("authenticated_itcm_record", DECODER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original = OTA.read_bytes()[0x20:]
itcm = module.decode_itcm(original)
with tempfile.TemporaryDirectory(prefix="g2-audio-itcm-copy-") as temp:
    binary = Path(temp) / "text.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "--only-section=.text",
                    str(OBJECT), str(binary)], check=True)
    compiled = binary.read_bytes()


def run(values, variant):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
    u.mem_map(0, 0x1000)
    u.mem_write(0x40, itcm)
    u.mem_map(0x438000, (len(original) + 4095) & ~4095)
    u.mem_write(0x438000, original)
    u.mem_map(0x100000, 0x1000)
    u.mem_write(0x100000, compiled)
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(0x20005000, struct.pack("<" + "I" * len(values), *values))
    u.mem_write(0x20006000, b"\xa5" * 128)
    u.reg_write(UC_ARM_REG_R0, 0x20005000)
    u.reg_write(UC_ARM_REG_R1, 0x20006000)
    u.reg_write(UC_ARM_REG_R2, len(values))
    u.reg_write(UC_ARM_REG_R7, 0x55aa55aa)
    u.reg_write(UC_ARM_REG_SP, 0x2007f000)
    u.reg_write(UC_ARM_REG_LR, 0x100101)
    writes = []
    u.hook_add(UC_HOOK_MEM_WRITE, lambda _u, _access, a, s, v, _data:
               writes.append([a, s, v]) if 0x20006000 <= a < 0x20006080 else None)
    u.emu_start(0x48086b if variant == "original" else 0x100001,
                0x100100, count=20000)
    return {"destination": bytes(u.mem_read(0x20006000, 128)).hex(),
            "source": bytes(u.mem_read(0x20005000, len(values) * 4)).hex(),
            "writes": writes, "sp": u.reg_read(UC_ARM_REG_SP),
            "pc": u.reg_read(UC_ARM_REG_PC)}


cases = []
for count in (1, 2, 5, 20):
    for salt in (0, 0xa5a5a5a5):
        values = [(salt + i) & 0xffffffff for i in range(count)]
        a = run(values, "original")
        b = run(values, "compiled")
        assert a == b, (count, salt, a, b)
        assert a["writes"] == [[0x20006000 + i * 4, 4, v]
                               for i, v in enumerate(values)]
        assert a["sp"] == 0x2007f000 and a["pc"] == 0x100100
        cases.append({"word_count": count, "salt": salt,
                      "original": a, "compiled": b, "match": True})

report = {"cases": cases, "matched": len(cases), "total": len(cases),
          "ota_sha256": hashlib.sha256(OTA.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
          "decoder_sha256": hashlib.sha256(DECODER.read_bytes()).hexdigest(),
          "decoded_itcm_sha256": hashlib.sha256(itcm).hexdigest(),
          "scope": "positive counts and nonoverlapping mapped buffers; original ITCM is authenticated OTA startup decoded; wrapper return register ignored by sole current caller"}
Path(__file__).with_name("itcm-copy-wrapper-execution.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(cases)}/{len(cases)} original/source ITCM copy wrapper comparisons pass")
