#!/usr/bin/env python3
"""Bind stock-compared Cordio ATT UUID range and comparison providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-atts-uuid-search-chain"
PRIOR = BASE / "main-ble-atts-set-attr/candidate.o"
SOURCES = [ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_atts_find_uuid_range_56d93c_20261017.c",
           ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_atts_uuid_compare_56c550_20261017.c"]
ORACLES = [BASE / "main-ble-atts-find-uuid-range/oracle-receipt.json",
           BASE / "main-ble-atts-uuid-compare/oracle-receipt.json"]
OBJECTS = [HERE / "find-uuid.o", HERE / "uuid-compare.o"]
CURRENT, OUT = HERE / "candidate.o", HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    cases = [360, 12]
    statuses = ["PASS_BOUNDED_MAIN_BLE_ATTS_FIND_UUID_RANGE_C",
                "PASS_BOUNDED_MAIN_BLE_ATTS_UUID_COMPARE_C"]
    for source, oracle_path, object_path, expected_cases, status in zip(
            SOURCES, ORACLES, OBJECTS, cases, statuses):
        oracle = json.loads(oracle_path.read_text())
        assert oracle["status"] == status
        assert oracle["cases"] == expected_cases and oracle["source_sha256"] == sha(source)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                        "-fno-builtin", "-c", str(source), "-o", str(object_path)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), *(str(o) for o in OBJECTS),
                    "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 110 and len(current) == 110
    assert removed == ["attsFindUuidInRange"] and added == ["attUuidCmp16to128"]
    assert {"attsFindUuidInRange", "attsUuidCmp"}.issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATTS_UUID_SEARCH_CHAIN_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "sources": [ref(path) for path in SOURCES],
        "oracles": [ref(path) for path in ORACLES], "oracle_cases": cases,
        "native_bodies": ["0x56d93c..0x56d9ec", "0x56c550..0x56c5aa"],
        "unresolved_before": 110, "unresolved_after": 110,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["attsFindUuidInRange", "attsUuidCmp"],
        "remaining_gate": "The ATT server UUID search and comparator match stock for 360 and 12 controlled cases; 16-to-128 conversion remains open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
