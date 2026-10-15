#!/usr/bin/env python3
"""Bind BLE DM native dispatcher and ten-row AppDb connection state."""
import json
import re
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_runtime_bindings.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-pair-runtime-state/apollo-main-master-pair-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-master-dm-runtime-bindings"
DISPATCH = "audio_ble_comm_dm_dispatch_a"
PROVIDER = "audio_ble_discovery_process_532924"
ROWS = "audio_ble_dm_conn_state_table_20067a30"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    disassembly = subprocess.check_output([
        "arm-none-eabi-objdump", "-d", "-M", "force-thumb",
        "--start-address=0x4b7d32", "--stop-address=0x4b7f00", str(NATIVE)], text=True)
    if "bl\t532924" not in disassembly:
        raise RuntimeError("native BLE communication call target changed")
    resolution = (G2 / "components/audio/uart_thread_source_candidate/display_ble_master_resolution_check.c").read_text()
    update = (G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_short.c").read_text()
    if "index>=10u" not in resolution or "(uint32_t)index*200u" not in resolution or \
       not re.search(r"i\s*<\s*10u", update) or "i * 200u + 0x84u" not in update:
        raise RuntimeError("ten-row source bounds changed")
    obj = OUT / "dm_runtime_bindings.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {DISPATCH, ROWS} or \
       names(obj, "-u") != {PROVIDER}:
        raise RuntimeError("DM C definitions or provider import changed")
    nm = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(line.split()[-1] == ROWS and int(line.split()[1], 16) == 2000
               for line in nm.splitlines() if len(line.split()) == 4):
        raise RuntimeError("DM connection state table size changed")
    before = names(BASE, "-u")
    if not {DISPATCH, ROWS} <= before or PROVIDER not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Main DM native contract or C provider absent")
    linked = OUT / "apollo-main-master-dm-runtime-bindings.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 474 or len(after) != 472 or \
       before - after != {DISPATCH, ROWS} or after - before:
        raise RuntimeError(f"unexpected Main DM import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_DM_RUNTIME_BINDINGS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_caller": "0x4b7d32", "native_provider": "0x532924",
               "native_table_origin": "0x20067a30", "table_rows": 10,
               "table_stride_bytes": 200, "table_bytes": 2000,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["This verifies native call target, C provider wiring, and source table dimensions.",
                          "Native absolute RAM placement and startup initialization remain unverified.",
                          "Full discovery behavior and physical hardware remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
