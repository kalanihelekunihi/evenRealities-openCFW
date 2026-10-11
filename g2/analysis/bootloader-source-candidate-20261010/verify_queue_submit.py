#!/usr/bin/env python3
"""Bounded original/source comparison for queue-submit wrapper 0x41649a."""
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
SOURCE_C = ROOT / "g2/components/bootloader/source_candidate_20261010/queue_submit_41649a.c"
ENTRY = 0x41649a
GUARD_STUB = 0x08002000
QUEUE_STUB = 0x08002020
BODY_SHA = "3da32489b13b78370fde01b22ef77515363ac2866a8baa24e444d03ae87ec0e9"


class Machine(v.Machine):
    def __init__(self, source, segments, symbols, guard, queue_result):
        super().__init__(source, segments, symbols)
        self.guard = guard
        self.queue_result = queue_result
        self.calls = []

    def code(self, cpu, pc, size, user):
        if pc == (GUARD_STUB if self.source else 0x41602a):
            self.calls.append(["guard"])
            self.ret(self.guard)
            return
        if pc == (QUEUE_STUB if self.source else 0x41937c):
            self.calls.append(["queue", *self.args(), self.u(cpu.reg_read(v.a.UC_ARM_REG_SP))])
            self.ret(self.queue_result)
            return
        super().code(cpu, pc, size, user)


def execute(machine, symbols, queue, item, r2, r3):
    cpu = machine.cpu
    for reg, value in zip([v.a.UC_ARM_REG_R0, v.a.UC_ARM_REG_R1,
                           v.a.UC_ARM_REG_R2, v.a.UC_ARM_REG_R3,
                           v.a.UC_ARM_REG_R4, v.a.UC_ARM_REG_R5],
                          [queue, item, r2, r3, 0x12345678, 0xabcdef01]):
        cpu.reg_write(reg, value)
    cpu.reg_write(v.a.UC_ARM_REG_SP, v.SP)
    cpu.reg_write(v.a.UC_ARM_REG_LR, v.STOP | 1)
    entry = (symbols["opencfw_provider_41649a"] & ~1) if machine.source else ENTRY
    cpu.emu_start(entry | 1, v.STOP + 2, count=1000)
    assert machine.finished
    return {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r4": cpu.reg_read(v.a.UC_ARM_REG_R4),
            "r5": cpu.reg_read(v.a.UC_ARM_REG_R5),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP), "calls": machine.calls}


def main():
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    assert hashlib.sha256(image[ENTRY-v.BASE:ENTRY-v.BASE+64]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-queue-source-") as temporary:
        obj = Path(temporary) / "queue.o"
        elf_path = Path(temporary) / "queue.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-mfloat-abi=softfp", "-O2", "-ffreestanding",
                        "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                        "-c", str(SOURCE_C), "-o", str(obj)], check=True)
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000",
                        "--defsym=opencfw_bl_context_guard=0x08002001",
                        "--defsym=opencfw_boot_queue_submit_raw=0x08002021",
                        "-e", "opencfw_provider_41649a", str(obj),
                        "-o", str(elf_path)], check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf_path)
        elf_hash = v.sha(elf_path)
    rows = []
    visited = set()
    for guard in [0, 1, 0xffffffff]:
        for queue, item in [(0, 0), (0x20001000, 0), (0, 0x20002000),
                            (0x20001000, 0x20002000)]:
            for lower in [0, 1, 2]:
                for r3 in [0, 0x13579bdf]:
                    pair = [Machine(False, (), {}, guard, lower),
                            Machine(True, segments, symbols, guard, lower)]
                    result = [execute(m, symbols, queue, item, 0x87654321, r3)
                              for m in pair]
                    assert result[0] == result[1], (guard, queue, item, lower, r3, result)
                    visited.update(pair[0].trace)
                    rows.append({"guard": guard, "queue": queue, "item": item,
                                 "lower": lower, "incoming_r3": r3, "observed": result[0]})
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "source_elf_sha256": elf_hash,
              "original_pcs": sorted(visited), "cases_detail": rows,
              "limits": "Context guard and lower queue function are controlled callbacks on both sides. "
                        "No queue ownership, scheduler execution, hardware behavior, or lower implementation proven."}
    Path(__file__).with_name("queue-submit-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows), "original_pcs": len(visited)}))


if __name__ == "__main__":
    main()
