#!/usr/bin/env python3
"""Compare stock 41602a guard with selected M55 C and historical alias."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ENTRY = 0x41602a
BODY_SHA = "e9208bab7b82a1d6f0228d69b2707c5cfadd5cb45b7d24963defe8cabb00b32b"
LOWER_ORIGINAL = 0x418b56
LOWER_SOURCE = 0x08005000
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_guard_alias.c"
PROVIDER = ROOT / "g2/components/bootloader/thread_creation/kernel_runtime.c"


def execute(source, segments, entry, lower, ipsr, mode, primask, basepri, r0, r1, r4):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_M33)
    for address, size in [(0x10000, 0x30000), (v.BASE, 0x30000),
                          (0x20000000, 0x40000), (v.STOP, 0x10000)]:
        cpu.mem_map(address, size)
    cset_pc = None
    if source:
        for segment in segments:
            if segment["data"]:
                cpu.mem_write(segment["address"], segment["data"])
                offset = segment["data"].find(bytes.fromhex("5fea0f90"))
                if offset >= 0:
                    assert cset_pc is None
                    cset_pc = segment["address"] + offset
        assert cset_pc is not None
        # The emulator lacks M55 CSET. Replace it only in emulator memory;
        # the linked source ELF and archived object remain untouched.
        cpu.mem_write(cset_pc, bytes.fromhex("00bf00bf"))
    else:
        cpu.mem_write(v.BASE, v.BLOB.read_bytes())
    lower_calls = []
    trace = {}
    finished = [False]

    def callback(uc, pc, size, _):
        if pc == v.STOP:
            finished[0] = True
            uc.emu_stop()
        elif pc == lower:
            lower_calls.append([uc.reg_read(v.a.UC_ARM_REG_R0),
                                uc.reg_read(v.a.UC_ARM_REG_R1)])
            uc.reg_write(v.a.UC_ARM_REG_R0, mode)
            uc.reg_write(v.a.UC_ARM_REG_PC, uc.reg_read(v.a.UC_ARM_REG_LR))
        elif source and pc == cset_pc:
            # Cortex-M55 CSET r0,ne is unsupported by this Unicorn M33 model.
            # Its architectural effect follows the preceding cmp's Z flag.
            zero = (uc.reg_read(v.a.UC_ARM_REG_CPSR) >> 30) & 1
            uc.reg_write(v.a.UC_ARM_REG_R0, 0 if zero else 1)
        elif not source and ENTRY <= pc < ENTRY + 46:
            trace[pc] = bytes(uc.mem_read(pc, size))

    cpu.hook_add(UC_HOOK_CODE, callback)
    for reg, value in [(v.a.UC_ARM_REG_IPSR, ipsr),
                       (v.a.UC_ARM_REG_PRIMASK, primask),
                       (v.a.UC_ARM_REG_BASEPRI, basepri),
                       (v.a.UC_ARM_REG_R0, r0), (v.a.UC_ARM_REG_R1, r1),
                       (v.a.UC_ARM_REG_R4, r4), (v.a.UC_ARM_REG_SP, v.SP),
                       (v.a.UC_ARM_REG_LR, v.STOP | 1)]:
        cpu.reg_write(reg, value)
    try:
        cpu.emu_start(entry | 1, v.STOP + 2, count=100)
    except Exception:
        pc = cpu.reg_read(v.a.UC_ARM_REG_PC)
        raise AssertionError(("execution fault", source, hex(pc), bytes(cpu.mem_read(pc & ~1, 4)).hex()))
    assert finished[0]
    result = {"r0": cpu.reg_read(v.a.UC_ARM_REG_R0), "r1": cpu.reg_read(v.a.UC_ARM_REG_R1),
            "r4": cpu.reg_read(v.a.UC_ARM_REG_R4), "sp": cpu.reg_read(v.a.UC_ARM_REG_SP),
            "ipsr": cpu.reg_read(v.a.UC_ARM_REG_IPSR),
            "primask": cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
            "basepri": cpu.reg_read(v.a.UC_ARM_REG_BASEPRI), "lower_calls": lower_calls}
    return result, trace


def main():
    assert v.sha(v.BLOB) == v.SHA
    original = v.BLOB.read_bytes()
    assert hashlib.sha256(original[ENTRY-v.BASE:ENTRY-v.BASE+46]).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-guard-alias-") as temporary:
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
                        "-e", "opencfw_provider_41602a",
                        "--defsym=opencfw_bl_queue_runtime_mode=0x08005001",
                        *(str(o) for o in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segments, symbols = v.elf.elf_info(elf)
        elf_hash = v.sha(elf)
    rows, visited = [], set()
    for ipsr in [0, 1, 16]:
        for mode in [0, 1, 2]:
            for primask in [0, 1]:
                for basepri in [0, 0x30]:
                    for r0 in [0, 0x12345678]:
                        r1, r4 = 0x55667788, 0x99aabbcc
                        stock, trace = execute(False, (), ENTRY, LOWER_ORIGINAL,
                                               ipsr, mode, primask, basepri, r0, r1, r4)
                        for address, instruction in trace.items():
                            visited.update(range(address, address + len(instruction)))
                        source, _ = execute(True, segments,
                                            symbols["opencfw_provider_41602a"] & ~1,
                                            LOWER_SOURCE, ipsr, mode, primask, basepri, r0, r1, r4)
                        assert stock == source, (ipsr, mode, primask, basepri, r0, stock, source)
                        rows.append({"ipsr": ipsr, "mode": mode, "primask": primask,
                                     "basepri": basepri, "r0": r0, "observed": stock})
    assert visited == set(range(ENTRY, ENTRY + 46)), sorted(set(range(ENTRY, ENTRY + 46)) - visited)
    report = {"status": "PASS", "cases": len(rows), "original_image_sha256": v.SHA,
              "original_body_sha256": BODY_SHA, "original_body_visited_bytes": len(visited),
              "source_elf_sha256": elf_hash, "comparisons": rows,
              "limits": "Scheduler-mode lower call is controlled. Unicorn M33 lacks the selected M55 CSET r0,ne instruction, so the harness applies its documented Z-flag effect at that one opcode. No live task or interrupt delivery."}
    Path(__file__).with_name("context-guard-alias-comparison.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "cases": len(rows)}))


if __name__ == "__main__":
    main()
