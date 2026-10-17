#!/usr/bin/env python3
"""Bind the stock-compared Cordio ATT client pending write callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-attc-write-cmd-callback"
PRIOR = BASE / "main-ble-atts-ind-pending/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_attc_write_cmd_callback_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "write-cmd.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATTC_WRITE_CMD_CALLBACK_C"
    assert oracle["cases"] == 48 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 111 and len(current) == 110
    assert removed == ["audio_ble_attc_write_cmd_callback_530de6"] and not added
    assert "audio_ble_attc_write_cmd_callback_530de6" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_BLE_ATTC_WRITE_CMD_CALLBACK_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 48,
        "native_bodies": ["0x530de6..0x530e30"],
        "unresolved_before": 111, "unresolved_after": 110,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_ble_attc_write_cmd_callback_530de6"],
        "remaining_gate": "The ATT client pending write callback matches stock for 48 valid-ABI cases; other ATT and Main imports remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
