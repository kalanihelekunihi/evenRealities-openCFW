#!/usr/bin/env python3
"""Bind four stock-matched Cordio DM connection action tables."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-dm-connection-action-tables"
PRIOR = BASE / "main-ble-atts-start-idle-timer/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_connection_action_tables_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "tables.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/stack/dm"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_MAIN_BLE_DM_CONNECTION_ACTION_TABLES_C"
    assert len(oracle["rows"]) == 4 and oracle["source_sha256"] == sha(SOURCE)
    upstream = [UPSTREAM / name for name in
                ("dm_conn_master_leg.c", "dm_conn_master.c",
                 "dm_conn_slave_leg.c", "dm_conn_slave.c")]
    markers = ("dmConnActSetMaster[]", "dmConnUpdActSetMaster[]",
               "dmConnActSetSlave[]", "dmConnUpdActSetSlave[]")
    assert all(marker in path.read_text() for path, marker in zip(upstream, markers))
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    expected_removed = sorted(("audio_ble_dm_master_table_a", "audio_ble_dm_master_table_b",
                               "audio_ble_dm_slave_table_a", "audio_ble_dm_slave_table_b"))
    expected_added = sorted({target for row in oracle["rows"]
                             for target in row["relocation_targets"]})
    assert len(prior) == 108 and len(current) == 114
    assert removed == expected_removed and added == expected_added
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_DM_CONNECTION_ACTION_TABLES_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "dependency_sources": [ref(path) for path in upstream],
        "stock_tables": oracle["rows"],
        "unresolved_before": 108, "unresolved_after": 114,
        "removed_imports": removed, "new_imports": added,
        "new_providers": removed,
        "remaining_gate": "Four Cordio DM connection action tables match stock pointer order; ten action bodies and final ROM placement remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
