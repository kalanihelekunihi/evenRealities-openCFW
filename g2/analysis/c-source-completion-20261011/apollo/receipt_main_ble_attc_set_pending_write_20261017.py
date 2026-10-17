#!/usr/bin/env python3
"""Bind stock-matched Cordio pending write-command slot provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-attc-set-pending-write"
PRIOR = BASE / "main-ble-attc-send-simple/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_attc_set_pending_write_530dbe_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "pending.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/stack/att/attc_main.c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATTC_SET_PENDING_WRITE_C"
    assert oracle["cases"] == 16 and oracle["source_sha256"] == sha(SOURCE)
    assert "attcSetPendWriteCmd" in UPSTREAM.read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    assert prior == current and len(current) == 109
    assert "audio_ble_attc_set_pending_write_530dbe" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_BLE_ATTC_SET_PENDING_WRITE_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "dependency_source": ref(UPSTREAM),
        "unresolved_before": 109, "unresolved_after": 109,
        "removed_imports": [], "new_imports": [],
        "new_providers": ["audio_ble_attc_set_pending_write_530dbe"],
        "remaining_gate": "One-slot pending write-command storage matches bounded stock behavior; its sender caller remains open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
