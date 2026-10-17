#!/usr/bin/env python3
"""Bind stock-matched HCI LE features and create-cancel providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-hci-le-features-cancel"
PRIOR = BASE / "main-ble-dm-slave-update-action/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_le_features_cancel_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "hci.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/hci/dual_chip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_HCI_LE_FEATURES_CANCEL_C"
    assert oracle["cases"] == 16 and oracle["source_sha256"] == sha(SOURCE)
    upstream = [UPSTREAM / "hci_core_ps.c", UPSTREAM / "hci_cmd.c"]
    assert "uint64_t HciGetLeSupFeat" in upstream[0].read_text()
    assert "void HciLeCreateConnCancelCmd" in upstream[1].read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    expected_removed = sorted(("audio_ble_hci_get_le_supported_features_530d3c",
                               "audio_ble_hci_create_conn_cancel_52b0a4"))
    assert removed == expected_removed and added == []
    assert len(prior) == 114 and len(current) == 112
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_HCI_LE_FEATURES_CANCEL_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "dependency_sources": [ref(path) for path in upstream],
        "unresolved_before": 114, "unresolved_after": 112,
        "removed_imports": removed, "new_imports": added,
        "new_providers": removed,
        "remaining_gate": "HCI LE feature mask and connection-cancel bodies are C-owned; command transport, controller-state placement and broader DM lower providers remain gated.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
