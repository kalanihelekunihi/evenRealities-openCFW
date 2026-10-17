#!/usr/bin/env python3
"""Bind stock-compared Cordio ATTS message setup and two local helpers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-atts-setup-msg"
PRIOR = BASE / "main-ble-atts-pend-ind-ntf/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_atts_setup_msg_5339ac_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "setup.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATTS_SETUP_MSG_C"
    assert oracle["cases"] == 48 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 109
    assert removed == ["audio_ble_atts_setup_msg_5339ac"]
    assert added == ["audio_ble_att_cfg_ptr_200004b4"]
    assert {"audio_ble_atts_setup_msg_5339ac",
            "audio_ble_att_msg_param_4b50f0",
            "audio_ble_atts_set_pend_ntf_53390e"}.issubset(
                symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATTS_SETUP_MSG_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 48,
        "native_bodies": ["0x53390e..0x533934", "0x5339ac..0x533a40",
                          "0x4b50f0..0x4b50fe"],
        "unresolved_before": 109, "unresolved_after": 109,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_ble_atts_setup_msg_5339ac",
                          "audio_ble_att_msg_param_4b50f0",
                          "audio_ble_atts_set_pend_ntf_53390e"],
        "remaining_gate": "The ATTS setup path matches stock for 48 controlled cases; ATT config-pointer RAM ownership and other Main imports remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
