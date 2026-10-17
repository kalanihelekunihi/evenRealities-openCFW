#!/usr/bin/env python3
"""Bind the stock-compared Cordio ATT indication message callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-atts-ind-msg"
PRIOR = BASE / "main-ble-att-uuid-16-to-128/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_atts_ind_msg_533bcc_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "ind-msg.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATTS_IND_MSG_C"
    assert oracle["cases"] == 64 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 111
    assert removed == ["audio_ble_atts_ind_msg_533bcc"]
    assert added == ["audio_ble_att_decode_msg_param_4b50fe",
                     "audio_ble_atts_pend_ind_ntf_5338ac",
                     "audio_ble_atts_setup_msg_5339ac"]
    assert "audio_ble_atts_ind_msg_533bcc" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_BLE_ATTS_IND_MSG_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 64,
        "native_bodies": ["0x533bcc..0x533c4c"],
        "unresolved_before": 109, "unresolved_after": 111,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_ble_atts_ind_msg_533bcc"],
        "remaining_gate": "The ATT indication message callback matches stock for 64 controlled cases; three lower helpers and other Main imports remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
