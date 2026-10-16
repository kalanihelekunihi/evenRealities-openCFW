#!/usr/bin/env python3
"""Bind source-owned BLE record rows and pair timestamp counter."""
import json
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_runtime_state.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-key-store/apollo-main-master-key-store.o"
OUT = G2 / "build/c-firmware/20261014/main-master-pair-runtime-state"
DISC = "audio_ble_discovery_connection_records_200717b0"
DM = "audio_ble_dm_conn_rows_200712a4"
COUNTER = "audio_ble_pair_timestamp_counter_20074344"
GROUPS = {DISC: (DISC, "audio_ble_atts_connection_rows"),
          DM: (DM, "audio_ble_connection_records", "audio_dm_connection_records")}
EXPECTED = {COUNTER, *(name for group in GROUPS.values() for name in group)}


def symbols(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(path)], text=True)
    result = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[2] in ("B", "D"):
            result[parts[3]] = (int(parts[0], 16), int(parts[1], 16))
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != EXPECTED or names(obj, "-u"):
        raise RuntimeError("runtime state definitions changed")
    table = symbols(obj)
    for base, group in GROUPS.items():
        expected_size = 0xc4 if base == DM else 0x90
        if any(table[name] != table[base] for name in group) or table[base][1] != expected_size:
            raise RuntimeError(f"record table aliases or dimensions differ: {base}")
    if table[COUNTER][1] != 4:
        raise RuntimeError("pair timestamp is not a 32-bit cell")
    before = names(BASE, "-u")
    if not EXPECTED <= before:
        raise RuntimeError("Main runtime state imports absent")
    linked = OUT / "apollo-main-master-pair-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != EXPECTED or after - before or len(before) != 480 or \
       len(after) != 474:
        raise RuntimeError(f"unexpected Main runtime state import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_addresses": {DISC: "0x200717b0", DM: "0x200712a4",
                                    COUNTER: "0x20074344"},
               "alias_groups": {key: list(value) for key, value in GROUPS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "discovery_table_bytes": 0x90, "dm_cb_storage_bytes": 0xc4,
               "dm_cb_record_bytes": 0x90, "counter_bytes": 4,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Record row count follows the three-slot master dispatcher and appNumConns C contracts; the extended DM block reaches the stock reset's highest observed write at offset 0xc3, not a proven whole-structure size.",
                          "Native absolute RAM placement and startup initialization remain unverified.",
                          "C aliases share storage within each table; hardware behavior remains unqualified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
