#!/usr/bin/env python3
"""Bind three stock-compared Cordio ATT control callbacks."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-att-control-callbacks"
PRIOR = BASE / "main-ble-att-interface-tables-785250/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_att_control_callbacks_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "att-control.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATT_CONTROL_CALLBACKS_C"
    assert oracle["cases"] == 30 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 112 and len(current) == 112
    assert removed == ["audio_ble_attc_ctrl_531330",
                       "audio_ble_atts_ctrl_534c8a",
                       "audio_ble_atts_ind_ctrl_533c4c"]
    assert added == ["audio_ble_attc_ind_confirm_4b5838",
                     "audio_ble_attc_write_cmd_callback_530de6",
                     "audio_ble_atts_ind_ntf_callback_53394c"]
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATT_CONTROL_CALLBACKS_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 30,
        "native_bodies": ["0x531330..0x53135a", "0x533c4c..0x533c6c",
                          "0x534c8a..0x534c9a"],
        "unresolved_before": 112, "unresolved_after": 112,
        "removed_imports": removed, "new_imports": added,
        "new_providers": removed,
        "remaining_gate": "Three ATT control callbacks match stock in 30 controlled cases. Their three pending-indication/write helpers and other Main imports remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
