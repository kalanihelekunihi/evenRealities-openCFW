#!/usr/bin/env python3
"""Compare the locked 22-byte tick wrapper with the source C provider."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
SOURCE_C = ROOT / "g2/components/bootloader/source_candidate_20261010/tick_accessor_4160e8.c"
ENTRY = 0x4160e8
GUARD_STUB = 0x08002000
BODY_SHA = "4fe35d35c5f61f5683c7ddd34f424d7f51d8a9276a0249c71b8473811dc7890a"


class Machine(v.Machine):
    def __init__(self, source, segments, symbols, guard_value):
        super().__init__(source, segments, symbols)
        self.guard_value = guard_value
        self.guard_calls = 0

    def code(self, cpu, pc, size, user):
        if pc == (GUARD_STUB if self.source else 0x41602a):
            self.guard_calls += 1
            self.ret(self.guard_value)
            return
        super().code(cpu, pc, size, user)


def run(machine, symbols, tick, r7):
    cpu = machine.cpu
    machine.w(0x20027148, tick)
    cpu.reg_write(v.a.UC_ARM_REG_R7, r7)
    cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    cpu.reg_write(v.a.UC_ARM_REG_R0, 0x12345678)
    cpu.reg_write(v.a.UC_ARM_REG_R1, 0xabcdef01)
    entry = (symbols["opencfw_provider_4160e8"] & ~1) if machine.source else ENTRY
    cpu.emu_start(entry | 1, v.STOP + 2, count=1000)
    assert machine.finished
    return {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r7": cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP),
            "tick": machine.u(0x20027148), "guard_calls": machine.guard_calls}


def main():
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    assert hashlib.sha256(image[ENTRY-v.BASE:ENTRY-v.BASE+22]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-tick-source-") as temporary:
        object_path = Path(temporary) / "tick.o"
        elf_path = Path(temporary) / "tick.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-mfloat-abi=softfp", "-O2", "-ffreestanding",
                        "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                        "-c", str(SOURCE_C), "-o", str(object_path)], check=True)
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000",
                        "--defsym=opencfw_bl_context_guard=0x08002001",
                        "-e", "opencfw_provider_4160e8", str(object_path),
                        "-o", str(elf_path)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf_path)
        source_elf_sha = v.sha(elf_path)
    rows = []
    visited = set()
    for guard in [0, 1, 0xffffffff]:
        for tick in [0, 1, 0x7fffffff, 0x80000000, 0xffffffff]:
            for r7 in [0, 0x12345678, 0xffffffff]:
                pair = [Machine(False, (), {}, guard), Machine(True, segments, symbols, guard)]
                actual = [run(pair[0], symbols, tick, r7), run(pair[1], symbols, tick, r7)]
                assert actual[0] == actual[1], (guard, tick, r7, actual)
                visited.update(pair[0].trace)
                rows.append({"guard": guard, "tick": tick, "r7": r7, "observed": actual[0]})
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "source_elf_sha256": source_elf_sha,
              "original_pcs": sorted(visited), "cases_detail": rows,
              "limits": "Guard is a controlled callback; original leaf getters execute. "
                        "No scheduler, interrupt delivery, hardware tick rate, or arbitrary caller state proven."}
    output = Path(__file__).with_name("tick-accessor-comparison.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": report["cases"],
                      "original_pcs": len(visited)}))


if __name__ == "__main__":
    main()
