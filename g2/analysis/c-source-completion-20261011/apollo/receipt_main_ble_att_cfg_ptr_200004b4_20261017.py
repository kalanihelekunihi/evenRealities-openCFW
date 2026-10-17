#!/usr/bin/env python3
"""Bind the startup-backed ATT configuration pointer cell."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-att-cfg-ptr-ram"
PRIOR = BASE / "main-ble-atts-setup-msg/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_att_cfg_ptr_200004b4_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "cfg-ptr.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_MAIN_BLE_ATT_CFG_PTR_RAM_SOURCE"
    assert oracle["stock_pointer"] == "0x20000414"
    assert oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 108
    assert removed == ["audio_ble_att_cfg_ptr_200004b4"] and not added
    assert "audio_ble_att_cfg_ptr_200004b4" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_BLE_ATT_CFG_PTR_RAM_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE),
        "native_cell": "0x200004b4", "native_initial_value": "0x20000414",
        "unresolved_before": 109, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_ble_att_cfg_ptr_200004b4"],
        "remaining_gate": "The ATT config-pointer initial word matches authenticated startup scatter; final RAM placement, target lifetime and other Main imports remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
