#!/usr/bin/env python3
"""Verify stock 41b2f8 alias and exact selected mask-provider instructions."""
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
ENTRY = 0x41b2f8
BODY_SHA = "f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323"
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/mask_interrupts_alias.c"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/kernel_runtime.c"


def execute(machine, entry, basepri, r0, r1, r2, r7):
    cpu = machine.cpu
    for reg, value in [(v.a.UC_ARM_REG_BASEPRI, basepri),
                       (v.a.UC_ARM_REG_R0, r0), (v.a.UC_ARM_REG_R1, r1),
                       (v.a.UC_ARM_REG_R2, r2), (v.a.UC_ARM_REG_R7, r7),
                       (v.a.UC_ARM_REG_SP, v.SP), (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    cpu.emu_start(entry | 1, v.STOP + 2, count=50)
    assert machine.finished
    return {"basepri": cpu.reg_read(v.a.UC_ARM_REG_BASEPRI),
            "r0": cpu.reg_read(v.a.UC_ARM_REG_R0), "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r2": cpu.reg_read(v.a.UC_ARM_REG_R2), "r7": cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB) == v.SHA
    original = v.BLOB.read_bytes()
    original_body = original[ENTRY-v.BASE:ENTRY-v.BASE+22]
    assert hashlib.sha256(original_body).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-mask-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "provider.o"]
        for src, obj in zip([ALIAS, PROVIDER], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-c", str(src), "-o", str(obj)], check=True)
        section = p / "selected-mask.bin"
        subprocess.run(["arm-none-eabi-objcopy",
                        f"--dump-section=.text.opencfw_bl_mask_interrupts={section}",
                        str(objects[1])], check=True)
        assert section.read_bytes() == original_body
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_provider_41b2f8", *(str(o) for o in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows, visited = [], set()
    for basepri in [0, 16, 48, 0x80, 0xff]:
        for r0 in [0, 0xabcdef01]:
            for r1 in [0, 0x12345678]:
                for r7 in [0, 0x87654321]:
                    r2 = 0x44556677
                    original_machine = v.Machine()
                    stock = execute(original_machine, ENTRY, basepri, r0, r1, r2, r7)
                    for pc, instruction in original_machine.trace.items():
                        address = int(pc, 16)
                        if ENTRY <= address < ENTRY + 22:
                            visited.update(range(address, address + len(instruction)//2))
                    source = execute(v.Machine(True, segments, symbols),
                                     symbols["opencfw_provider_41b2f8"] & ~1,
                                     basepri, r0, r1, r2, r7)
                    assert stock == source, (basepri, r0, r1, r7, stock, source)
                    rows.append({"basepri": basepri, "r0": r0, "r1": r1,
                                 "r7": r7, "observed": stock})
    assert visited == set(range(ENTRY, ENTRY + 22))
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "selected_body_byte_identical": True,
              "original_body_visited_bytes": len(visited), "source_elf_sha256": elf_hash,
              "cases_detail": rows,
              "limits": "Unicorn BASEPRI and register comparison; interrupt-delivery timing and hardware behavior unmeasured."}
    Path(__file__).with_name("mask-interrupts-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
