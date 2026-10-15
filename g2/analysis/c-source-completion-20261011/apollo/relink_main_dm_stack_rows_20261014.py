#!/usr/bin/env python3
"""Relink the stale inlined DM-row bodies to the corrected C state object."""
import json
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261014/main-hci-cmd-state/apollo-main-hci-cmd-state.o"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_stack_lowers.c"
OVERLAY = G2 / "analysis/c-source-completion-20261011/apollo/dm_stack_row_relink_overlay.c"
OUT = G2 / "build/c-firmware/20261014/main-dm-row-relink"
SYMBOLS = {"audio_ble_stack_lower_5369ea", "audio_ble_dm_stack_state_init"}
ROWS = "audio_ble_dm_stack_rows_200738dc"


def run(*args):
    subprocess.run(args, check=True)


def globals_at(path):
    result = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[-1] in SYMBOLS:
            result[parts[-1]] = (int(parts[0], 16), parts[1])
    return result


def main():
    source = SOURCE.read_text()
    overlay = OVERLAY.read_text()
    for expected in ("uint8_t *rows=audio_ble_dm_stack_rows_200738dc;",
                     "rows[0x18u]=0u;", "audio_ble_dm_stack_state_init();"):
        if expected not in source or expected not in overlay:
            raise RuntimeError(f"DM-row source/overlay contract changed: {expected}")
    if globals_at(BASE).keys() != SYMBOLS or ROWS not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("base DM-row symbol contract changed")
    prior_reloc = subprocess.check_output(["arm-none-eabi-objdump", "-r", str(BASE)], text=True)
    if prior_reloc.count("R_ARM_THM_CALL    audio_ble_stack_lower_5369ea") != 1:
        raise RuntimeError("old stack-lower call site changed")
    OUT.mkdir(parents=True, exist_ok=True)
    weak, obj, linked = (OUT / name for name in
                         ("apollo-main-weak.o", "dm_stack_row_relink_overlay.o",
                          "apollo-main-dm-row-relink.o"))
    run("arm-none-eabi-objcopy", *(f"--weaken-symbol={name}" for name in sorted(SYMBOLS)),
        str(BASE), str(weak))
    run("clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
        "-Wextra", "-Werror", "-c", str(OVERLAY), "-o", str(obj))
    if names(obj, "-g", "--defined-only") != SYMBOLS or names(obj, "-u") != {
            "WsfTaskLock", "WsfTaskUnlock", "audio_ble_dm_config",
            "audio_ble_dm_privacy_state", "audio_ble_dm_stack_rows_200738dc",
            "audio_ble_dm_stack_table_78a88c"}:
        raise RuntimeError("overlay C symbol contract changed")
    run("arm-none-eabi-ld", "-r", str(weak), str(obj), "-o", str(linked))
    before, after = names(BASE, "-u"), names(linked, "-u")
    if before != after:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    old, new = globals_at(BASE), globals_at(linked)
    if set(new) != SYMBOLS or any(new[name][1] != "T" or
                                  new[name][0] == old[name][0] for name in SYMBOLS):
        raise RuntimeError("strong corrected function definitions not selected")
    reloc = subprocess.check_output(["arm-none-eabi-objdump", "-r", str(linked)], text=True)
    if reloc.count("R_ARM_THM_CALL    audio_ble_stack_lower_5369ea") != 1 or \
       reloc.count("R_ARM_THM_MOVW_ABS_NC  audio_ble_dm_stack_rows_200738dc") < 2 or \
       reloc.count("R_ARM_THM_MOVT_ABS  audio_ble_dm_stack_rows_200738dc") < 2:
        raise RuntimeError("corrected call/DM-row relocations missing")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_ROW_RELINK_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "overlay": str(OVERLAY.relative_to(ROOT)), "overlay_sha256": sha(OVERLAY),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "weak_object": str(weak.relative_to(ROOT)), "weak_sha256": sha(weak),
               "overlay_object": str(obj.relative_to(ROOT)), "overlay_object_sha256": sha(obj),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "replaced_symbols": sorted(SYMBOLS),
               "strong_replacement_offsets": {name: hex(new[name][0]) for name in sorted(SYMBOLS)},
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "limits": ["This is a relocatable overlay; stale function bytes remain in the aggregate object but exported calls resolve to corrected strong C bodies.",
                          "A full root archive rebuild from current source is still required before final image linkage.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
