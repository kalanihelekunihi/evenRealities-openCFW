#!/usr/bin/env python3
"""Bind five bounded stock-matched Cordio DM connection actions."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-dm-connection-actions-followup"
PRIOR = BASE / "main-ble-dm-connection-actions-small/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_connection_actions_followup_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "actions.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_DM_CONNECTION_ACTIONS_FOLLOWUP_C"
    assert oracle["cases"] == 25 and oracle["source_sha256"] == sha(SOURCE)
    upstream = [UPSTREAM / name for name in
                ("dm_conn_master.c", "dm_conn_slave_leg.c", "dm_conn_slave.c")]
    markers = ("void dmConnUpdActL2cUpdateInd", "void dmConnSmActCancelAccept",
               "void dmConnSmActConnAccepted", "void dmConnSmActAcceptFailed",
               "void dmConnUpdActL2cUpdateCnf")
    assert all(any(marker in path.read_text() for path in upstream) for marker in markers)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    expected_removed = sorted(oracle["actions"])
    expected_added = sorted(("audio_ble_dm_adv_stop_directed_4ba864",
                             "audio_ble_dm_adv_connected_4ba9d4",
                             "audio_ble_dm_adv_connect_failed_4bab04",
                             "audio_ble_dm_slave_update_response_56e4f8"))
    assert removed == expected_removed and added == expected_added
    assert len(prior) == 114 and len(current) == 113
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_DM_CONNECTION_ACTIONS_FOLLOWUP_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "dependency_sources": [ref(path) for path in upstream],
        "unresolved_before": 114, "unresolved_after": 113,
        "removed_imports": removed, "new_imports": added,
        "new_providers": removed,
        "remaining_gate": "Nine DM connection actions match stock call boundaries; one slave update action, lower providers, and final ROM placement remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
