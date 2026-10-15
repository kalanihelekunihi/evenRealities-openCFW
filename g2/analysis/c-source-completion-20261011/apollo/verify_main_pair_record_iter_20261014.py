#!/usr/bin/env python3
"""Compare native/C AppDb iteration, including continuation scan bounds."""
import json
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_record_iter.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-security-request/apollo-main-slave-security-request.o"
OUT = G2 / "build/c-firmware/20261014/main-pair-record-iter"
ENTRY = "audio_ble_pair_record_next_47a630"
TABLE, STOP = 0x20067a30, 0x10010000


def run(segments, entry, current, occupied):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    for index in occupied:
        uc.mem_write(TABLE + index * 200 + 0x2f, b"\x01")
    uc.reg_write(UC_ARM_REG_R0, current)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=200)
    return uc.reg_read(UC_ARM_REG_R0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_record_iter.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != {"audio_ble_dm_conn_state_table_20067a30"}:
        raise RuntimeError("pair iterator source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "iter.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        f"--defsym=audio_ble_dm_conn_state_table_20067a30={TABLE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        sets = [(), (0,), (1,), (9,), (10,), (17,), (0, 5, 9), (4, 5, 10),
                tuple(range(18))]
        cases = [(current, occupied) for current in (0, *(TABLE+i*200 for i in range(10)))
                 for occupied in sets]
        for current, occupied in cases:
            native = run(native_segments, 0x47a630, current, occupied)
            compiled = run(native_segments + source_segments, symbols[ENTRY], current, occupied)
            if native != compiled:
                raise RuntimeError(f"pair iterator mismatch {(current, occupied)}: {native:#x} != {compiled:#x}")
    before = names(BASE, "-u")
    if "audio_ble_dm_conn_state_table_20067a30" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main AppDb table contract changed")
    linked = OUT / "apollo-main-pair-record-iter.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if after != before:
        raise RuntimeError("unexpected pair iterator import delta")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAIR_RECORD_ITER_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x47a630", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The iterator C body is prepared for a downstream slave fallback provider.",
                          "Native continuation may inspect RAM beyond the ten-row table.",
                          "Absolute RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
