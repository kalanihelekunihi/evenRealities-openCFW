#!/usr/bin/env python3
"""Compare historical CPACR alias with selected source-owned assembly."""
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
ENTRY = 0x41ac44
BODY_SHA = "5877e91ed2ac36963349599d01147dfe5743eb4b8374717bf3b9676254387d2a"
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/coprocessor_enable_alias.c"
NATIVE = ROOT / "g2/components/bootloader/platform_startup/local_providers.S"
CPACR = 0xe000ed88


def execute(machine, entry, cpacr, r0, r1, r7):
    cpu = machine.cpu
    machine.w(CPACR, cpacr)
    for reg, value in [(v.a.UC_ARM_REG_R0, r0), (v.a.UC_ARM_REG_R1, r1),
                       (v.a.UC_ARM_REG_R7, r7), (v.a.UC_ARM_REG_SP, v.SP),
                       (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"cpacr": machine.u(CPACR), "r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r1": cpu.reg_read(v.a.UC_ARM_REG_R1), "r7": cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB) == v.SHA
    original = v.BLOB.read_bytes()
    assert hashlib.sha256(original[ENTRY-v.BASE:ENTRY-v.BASE+22]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-coprocessor-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "native.o"]
        for src, obj in zip([ALIAS, NATIVE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-O2",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-c", str(src), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_provider_41ac44", *(str(o) for o in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows = []
    visited = set()
    for cpacr in [0, 0x00f00000, 0xff000000, 0x12345678]:
        for r0 in [0, 0xabcdef01]:
            for r1 in [0, 0x13579bdf]:
                for r7 in [0, 0x87654321]:
                    original_machine = v.Machine()
                    stock = execute(original_machine, ENTRY, cpacr, r0, r1, r7)
                    for pc, instruction in original_machine.trace.items():
                        address = int(pc, 16)
                        if ENTRY <= address < ENTRY + 22:
                            visited.update(range(address, address + len(instruction)//2))
                    source = execute(v.Machine(True, segments, symbols),
                                     symbols["opencfw_provider_41ac44"] & ~1,
                                     cpacr, r0, r1, r7)
                    assert stock == source, (cpacr, r0, r1, r7, stock, source)
                    rows.append({"cpacr": cpacr, "r0": r0, "r1": r1,
                                 "r7": r7, "observed": stock})
    assert visited == set(range(ENTRY, ENTRY + 22)), sorted(set(range(ENTRY, ENTRY + 22)) - visited)
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "source_elf_sha256": elf_hash,
              "original_body_visited_bytes": len(visited), "cases_detail": rows,
              "limits": "Unicorn compares CPACR and register state; FPU enablement on physical hardware is not measured."}
    Path(__file__).with_name("coprocessor-enable-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
