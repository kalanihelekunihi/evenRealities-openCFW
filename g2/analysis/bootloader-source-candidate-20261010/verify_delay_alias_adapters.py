#!/usr/bin/env python3
"""Compare historical delay alias adapters with authenticated stock wrappers."""
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
ADAPTER = ROOT / "g2/components/bootloader/source_candidate_20261010/delay_alias_adapters.c"
NATIVE = ROOT / "g2/components/bootloader/platform_startup/local_providers.S"
LOWER_ORIGINAL = 0x41d1c0
LOWER_SOURCE = 0x08005000
BODIES = {
    "opencfw_bl_delay": (0x41f9d8, 14, "f9d267ca0fe9273e71065d8d35b31cf4d296067d79e9787d7635113ae2ab6676"),
    "opencfw_bl_delay_raw": (0x41f9e6, 8, "dddd4579356bb2192ab70e96b40e55aed4767132acd66a48667053c1045ec591"),
    "opencfw_provider_41f9d8": (0x41f9d8, 14, "f9d267ca0fe9273e71065d8d35b31cf4d296067d79e9787d7635113ae2ab6676"),
}


def execute(machine, entry, lower, r0, r1, r7):
    cpu = machine.cpu
    machine.exec_ranges.append((lower, lower + 2))
    calls = []

    def callback(uc, pc, size, _):
        if pc == lower:
            calls.append([uc.reg_read(v.a.UC_ARM_REG_R0), uc.reg_read(v.a.UC_ARM_REG_R1)])
            uc.reg_write(v.a.UC_ARM_REG_R0, 0xface1234)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))

    cpu.hook_add(v.UC_HOOK_CODE, callback)
    cpu.reg_write(v.a.UC_ARM_REG_R0, r0)
    cpu.reg_write(v.a.UC_ARM_REG_R1, r1)
    cpu.reg_write(v.a.UC_ARM_REG_R7, r7)
    cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"calls": calls, "r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r1": cpu.reg_read(v.a.UC_ARM_REG_R1), "r7": cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    for entry, length, digest in BODIES.values():
        actual = hashlib.sha256(image[entry-v.BASE:entry-v.BASE+length]).hexdigest()
        if digest is not None:
            assert actual == digest
    with tempfile.TemporaryDirectory(prefix="bootloader-delay-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "adapter.o", p / "native.o"]
        for source, obj in zip([ADAPTER, NATIVE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_bl_delay", "-u", "opencfw_bl_delay_raw",
                        "-u", "opencfw_provider_41f9d8",
                        "--defsym=opencfw_hal_delay_us=0x08005001",
                        *(str(o) for o in objects), "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    cases = []
    for alias, (entry, length, _) in BODIES.items():
        assert alias in symbols, alias
        for r0 in [0, 1, 0x1234, 0xffffffff]:
            for r1 in [0, 0x12345678]:
                for r7 in [0, 0x87654321]:
                    original = execute(v.Machine(), entry, LOWER_ORIGINAL, r0, r1, r7)
                    source = execute(v.Machine(True, segments, symbols), symbols[alias] & ~1,
                                     LOWER_SOURCE, r0, r1, r7)
                    assert original == source, (alias, r0, r1, r7, original, source)
                    cases.append({"alias": alias, "r0": r0, "r1": r1, "r7": r7,
                                  "observed": original})
    report = {"status": "PASS", "cases": len(cases), "original_image_sha256": v.SHA,
              "original_bodies": {hex(entry): {"length": length,
                  "sha256": hashlib.sha256(image[entry-v.BASE:entry-v.BASE+length]).hexdigest()}
                  for entry, length, _ in BODIES.values()},
              "source_elf_sha256": elf_hash, "cases_detail": cases,
              "limits": "Unicorn register/callback comparison; lower delay timing and hardware not measured."}
    Path(__file__).with_name("delay-alias-adapters-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(cases)}))


if __name__ == "__main__":
    main()
