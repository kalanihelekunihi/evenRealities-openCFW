#!/usr/bin/env python3
"""Compare the C alias plus authored ASM with original critical-save leaf."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ENTRY = 0x41b8ec
BODY_SHA = "720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf"
ADAPTER = ROOT / "g2/components/bootloader/source_candidate_20261010/critical_save_adapter.c"
NATIVE = ROOT / "g2/components/bootloader/platform_control/critical_save.S"


def execute(machine, entry, primask, r0, r1):
    cpu = machine.cpu
    cpu.reg_write(v.a.UC_ARM_REG_PRIMASK, primask)
    cpu.reg_write(v.a.UC_ARM_REG_R0, r0)
    cpu.reg_write(v.a.UC_ARM_REG_R1, r1)
    cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "primask": cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    assert hashlib.sha256(image[ENTRY-v.BASE:ENTRY-v.BASE+8]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-critical-alias-") as temporary:
        p = Path(temporary)
        objs = [p / "adapter.o", p / "native.o"]
        for source, obj in zip([ADAPTER, NATIVE], objs):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-O2", "-ffreestanding", "-fno-builtin",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "-e",
                        "opencfw_bl_critical_save", *(str(o) for o in objs),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    cases = []
    original_pcs = set()
    for primask in [0, 1]:
        for r0 in [0, 0x12345678, 0xffffffff]:
            for r1 in [0, 0xabcdef01]:
                original = v.Machine()
                source = v.Machine(True, segments, symbols)
                got = [execute(original, ENTRY, primask, r0, r1),
                       execute(source, symbols["opencfw_bl_critical_save"] & ~1,
                               primask, r0, r1)]
                assert got[0] == got[1], (primask, r0, r1, got)
                original_pcs.update(original.trace)
                cases.append({"primask": primask, "r0": r0, "r1": r1, "observed": got[0]})
    report = {"status": "PASS", "cases": len(cases), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "source_elf_sha256": elf_hash,
              "original_pcs": sorted(original_pcs), "cases_detail": cases,
              "limits": "Architectural PRIMASK behavior in Unicorn only; no physical ISR timing."}
    Path(__file__).with_name("critical-save-adapter-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(cases), "original_pcs": len(original_pcs)}))


if __name__ == "__main__":
    main()
