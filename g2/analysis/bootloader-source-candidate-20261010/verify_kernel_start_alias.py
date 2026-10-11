#!/usr/bin/env python3
"""Compare original 4160b0 startup and selected C through caller alias."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ENTRY = 0x4160b0
BODY_SHA = "e5df2dd5abb60c81887e7754bca2eef18621d559e28482dcce5ffaf887993678"
STATE = 0x200270d4
GUARD_ORIGINAL, MODE_ORIGINAL = 0x41602a, 0x418b56
GUARD_SOURCE, MODE_SOURCE = 0x08005000, 0x08005010
START_ORIGINAL, START_SOURCE = 0x418148, 0x08005020
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/kernel_start_alias.c"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/lifecycle.c"


def execute(machine, entry, guard_addr, mode_addr, start_addr, guard, mode, state, r0, r1, r7):
    cpu = machine.cpu
    machine.exec_ranges.extend([(guard_addr, guard_addr + 2), (mode_addr, mode_addr + 2),
                                (start_addr, start_addr + 2)])
    machine.w(STATE, state)
    calls, writes = [], []

    def callback(uc, pc, size, _):
        if pc in (guard_addr, mode_addr, start_addr):
            name = "guard" if pc == guard_addr else "mode" if pc == mode_addr else "start"
            calls.append([name, machine.u(STATE)])
            uc.reg_write(v.a.UC_ARM_REG_R0,
                         guard if pc == guard_addr else mode if pc == mode_addr else 0)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))

    def write(uc, access, address, size, value, _):
        if address == STATE:
            writes.append([size, value])

    cpu.hook_add(v.UC_HOOK_CODE, callback)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    for reg, value in [(v.a.UC_ARM_REG_R0, r0), (v.a.UC_ARM_REG_R1, r1),
                       (v.a.UC_ARM_REG_R4, 0x44556677),
                       (v.a.UC_ARM_REG_R7, r7), (v.a.UC_ARM_REG_SP, v.SP),
                       (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0),
            "r4": cpu.reg_read(v.a.UC_ARM_REG_R4),
            "r7": cpu.reg_read(v.a.UC_ARM_REG_R7), "sp": cpu.reg_read(v.a.UC_ARM_REG_SP),
            "state": machine.u(STATE), "writes": writes, "calls": calls}


def main():
    assert v.sha(v.BLOB) == v.SHA
    image = v.BLOB.read_bytes()
    assert hashlib.sha256(image[ENTRY-v.BASE:ENTRY-v.BASE+56]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-kernel-start-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "provider.o"]
        for src, obj in zip([ALIAS, PROVIDER], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-c", str(src), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_provider_4160b0",
                        "--defsym=opencfw_bl_context_guard=0x08005001",
                        "--defsym=opencfw_bl_queue_runtime_mode=0x08005011",
                        "--defsym=opencfw_bl_kernel_start=0x08005021",
                        *(str(o) for o in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows, visited = [], set()
    for guard in [0, 1, 0xffffffff]:
        for mode in [0, 1, 2]:
            for state in [0, 1, 2]:
                for r0 in [0, 0x12345678]:
                    for r7 in [0, 0x87654321]:
                        r1 = 0x55667788
                        original = v.Machine()
                        stock = execute(original, ENTRY, GUARD_ORIGINAL, MODE_ORIGINAL, START_ORIGINAL,
                                        guard, mode, state, r0, r1, r7)
                        for pc, instruction in original.trace.items():
                            address = int(pc, 16)
                            if ENTRY <= address < ENTRY + 56:
                                visited.update(range(address, address + len(instruction)//2))
                        source = execute(v.Machine(True, segments, symbols),
                                         symbols["opencfw_provider_4160b0"] & ~1,
                                         GUARD_SOURCE, MODE_SOURCE, START_SOURCE,
                                         guard, mode, state, r0, r1, r7)
                        assert stock == source, (guard, mode, state, r0, r7, stock, source)
                        rows.append({"guard": guard, "mode": mode, "state": state,
                                     "r0": r0, "r7": r7, "observed": stock})
    assert visited == set(range(ENTRY, ENTRY + 56))
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "original_body_visited_bytes": len(visited),
              "source_elf_sha256": elf_hash, "comparisons": rows,
              "limits": "Context guard, mode, and zero-argument scheduler-start calls are controlled boundaries; incidental input/output R1 and scheduler-start R0 arguments are excluded from the void caller ABI. No live scheduler or interrupt delivery."}
    Path(__file__).with_name("kernel-start-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
