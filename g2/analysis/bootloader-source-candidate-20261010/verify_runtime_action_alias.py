#!/usr/bin/env python3
"""Check stock 416200 ABI through the selected C provider and new C alias."""
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
ENTRY = 0x416200
BODY_SHA = "e4c78725081eb02641d1918a3879468520998e6bc55183b1115b2f130a39bf28"
GUARD_ORIGINAL = 0x41602a
GUARD_SOURCE = 0x08005000
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/runtime_action_alias.c"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/thread_termination.c"
LEGACY = ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/runtime-action-416200/runtime_action.c"


def execute(machine, entry, guard_addr, guard_result, handle, r3):
    machine.exec_ranges.append((guard_addr, guard_addr + 2))
    cpu = machine.cpu
    guard_calls = []

    def guard(uc, pc, size, _):
        if pc == guard_addr:
            guard_calls.append([uc.reg_read(v.a.UC_ARM_REG_R0), uc.reg_read(v.a.UC_ARM_REG_R3)])
            uc.reg_write(v.a.UC_ARM_REG_R0, guard_result)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))

    cpu.hook_add(v.UC_HOOK_CODE, guard)
    for reg, value in [(v.a.UC_ARM_REG_R0, handle), (v.a.UC_ARM_REG_R1, 0x11223344),
                       (v.a.UC_ARM_REG_R2, 0x55667788), (v.a.UC_ARM_REG_R3, r3),
                       (v.a.UC_ARM_REG_R4, 0x44556677), (v.a.UC_ARM_REG_R7, 0x778899aa),
                       (v.a.UC_ARM_REG_SP, v.SP), (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    assert machine.finished
    return {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0), "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r4": cpu.reg_read(v.a.UC_ARM_REG_R4), "r7": cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp": cpu.reg_read(v.a.UC_ARM_REG_SP), "guard_calls": guard_calls}


def main():
    assert v.sha(v.BLOB) == v.SHA
    original = v.BLOB.read_bytes()
    assert hashlib.sha256(original[ENTRY-v.BASE:ENTRY-v.BASE+58]).hexdigest() == BODY_SHA
    assert PROVIDER.read_bytes() == LEGACY.read_bytes()
    with tempfile.TemporaryDirectory(prefix="bootloader-runtime-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "provider.o"]
        for src, obj in zip([ALIAS, PROVIDER], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-c", str(src), "-o", str(obj)], check=True)
        externs = ["opencfw_bl_context_guard", "opencfw_bl_kernel_enter",
                   "opencfw_bl_kernel_exit", "opencfw_bl_kernel_reschedule",
                   "opencfw_bl_mask_interrupts", "opencfw_bl_rtos_free",
                   "opencfw_boot_list_unlink", "opencfw_boot_next_unblock_refresh"]
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_provider_416200", "-u", "opencfw_boot_dfu_thread_terminate",
                        *(f"--defsym={name}=0x08005001" for name in externs),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows = []
    for alias in ["opencfw_provider_416200", "opencfw_boot_dfu_thread_terminate"]:
        assert alias in symbols
        for guard_result in [0, 1, 0xffffffff]:
            for handle in [0, 0x20003000]:
                if guard_result == 0 and handle != 0:
                    continue  # non-null path requires state/delete providers; legacy suite covers it
                for r3 in [0, 0x99aabbcc, 0xffffffff]:
                    stock = execute(v.Machine(), ENTRY, GUARD_ORIGINAL, guard_result, handle, r3)
                    source = execute(v.Machine(True, segments, symbols),
                                     symbols[alias] & ~1,
                                     GUARD_SOURCE, guard_result, handle, r3)
                    assert stock == source, (alias, guard_result, handle, r3, stock, source)
                    rows.append({"alias": alias, "guard_result": guard_result,
                                 "handle": handle, "r3": r3, "observed": stock})
    result = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "selected_provider_sha256": v.sha(PROVIDER),
              "source_elf_sha256": elf_hash, "cases_detail": rows,
              "limits": "C alias ABI checked on guard rejection/null branches; preexisting 260-case legacy suite covers the identical provider source's other paths at its earlier compiler configuration."}
    Path(__file__).with_name("runtime-action-alias-comparison.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
