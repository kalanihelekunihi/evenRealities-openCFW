#!/usr/bin/env python3
"""Compare original FP lazy-mode wrapper and historical C-source alias."""
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
ENTRY = 0x41ac5a
BODY_SHA = "06f514f45185357f5e672d6abde447b7fec542c056e0ca33b8101e900a1bc8c8"
FPCCR = 0xe000ef34
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/fp_lazy_mode_alias.c"
NATIVE = ROOT / "g2/components/bootloader/platform_startup/local_providers.S"
CRITICAL = ROOT / "g2/components/bootloader/platform_control/critical_save.S"


def execute(machine, entry, mode, fpccr, primask, r1, r2, r3, r4):
    cpu = machine.cpu
    machine.w(FPCCR, fpccr)
    for reg, value in [(v.a.UC_ARM_REG_R0, mode), (v.a.UC_ARM_REG_R1, r1),
                       (v.a.UC_ARM_REG_R2, r2), (v.a.UC_ARM_REG_R3, r3),
                       (v.a.UC_ARM_REG_R4, r4), (v.a.UC_ARM_REG_PRIMASK, primask),
                       (v.a.UC_ARM_REG_SP, v.SP), (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"fpccr": machine.u(FPCCR), "primask": cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
            "r0": cpu.reg_read(v.a.UC_ARM_REG_R0), "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r2": cpu.reg_read(v.a.UC_ARM_REG_R2), "r3": cpu.reg_read(v.a.UC_ARM_REG_R3),
            "r4": cpu.reg_read(v.a.UC_ARM_REG_R4), "sp": cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB) == v.SHA
    original = v.BLOB.read_bytes()
    assert hashlib.sha256(original[ENTRY-v.BASE:ENTRY-v.BASE+48]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-fp-lazy-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "native.o", p / "critical.o"]
        for src, obj in zip([ALIAS, NATIVE, CRITICAL], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-O2",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-c", str(src), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_provider_41ac5a", *(str(o) for o in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows, visited = [], set()
    for mode in [0, 1, 0x100, 0x101, 0xffffffff]:
        for fpccr in [0, 0x40000000, 0x80000000, 0xc0001234]:
            for primask in [0, 1]:
                for r3 in [0, 0xabcdef12]:
                    r1, r2, r4 = 0x11223344, 0x55667788, 0x44556677
                    original_machine = v.Machine()
                    stock = execute(original_machine, ENTRY, mode, fpccr, primask,
                                    r1, r2, r3, r4)
                    for pc, instruction in original_machine.trace.items():
                        address = int(pc, 16)
                        if ENTRY <= address < ENTRY + 48:
                            visited.update(range(address, address + len(instruction)//2))
                    source = execute(v.Machine(True, segments, symbols),
                                     symbols["opencfw_provider_41ac5a"] & ~1,
                                     mode, fpccr, primask, r1, r2, r3, r4)
                    assert stock == source, (mode, fpccr, primask, r3, stock, source)
                    rows.append({"mode": mode, "fpccr": fpccr, "primask": primask,
                                 "r3": r3, "observed": stock})
    assert visited == set(range(ENTRY, ENTRY + 48)), sorted(set(range(ENTRY, ENTRY + 48)) - visited)
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "original_body_visited_bytes": len(visited),
              "source_elf_sha256": elf_hash, "cases_detail": rows,
              "limits": "Unicorn compares FPCCR, PRIMASK and registers; physical FPU exception behavior remains unmeasured."}
    Path(__file__).with_name("fp-lazy-mode-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
