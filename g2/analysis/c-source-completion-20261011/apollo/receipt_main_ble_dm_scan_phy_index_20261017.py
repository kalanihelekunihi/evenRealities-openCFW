#!/usr/bin/env python3
"""Bind stock-matched Cordio scanner PHY index provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-dm-scan-phy-index"
PRIOR = BASE / "main-ble-dm-conn-open/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_dm_scan_phy_index_4d2b3e_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "phy.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/stack/dm/dm_main.c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_MAIN_BLE_DM_SCAN_PHY_INDEX_C"
    assert oracle["cases"] == 42 and oracle["source_sha256"] == sha(SOURCE)
    assert "DmScanPhyToIdx" in UPSTREAM.read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert removed == ["audio_ble_dm_scan_phy_index_4d2b3e"] and added == []
    assert len(prior) == 111 and len(current) == 110
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_DM_SCAN_PHY_INDEX_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "dependency_source": ref(UPSTREAM),
        "unresolved_before": 111, "unresolved_after": 110,
        "removed_imports": removed, "new_imports": added, "new_providers": removed,
        "remaining_gate": "Cordio scan PHY index helper and wrapper match stock input/output mappings; HCI create connection and other lower providers remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
