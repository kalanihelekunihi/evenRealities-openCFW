#!/usr/bin/env python3
"""Bind bounded Cordio ATT response dispatcher and expose its child imports."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-ble-attc-proc-rsp"
PRIOR = BASE / "main-ble-attc-proc-ind/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_attc_proc_rsp_4b5448_20261017.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "proc-rsp.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
UPSTREAM = ROOT / "third-party/upstream/cordio/ble-host/sources/stack/att/attc_proc.c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_BOUNDED_MAIN_BLE_ATTC_PROC_RSP_C"
    assert oracle["cases"] == 245 and oracle["source_sha256"] == sha(SOURCE)
    assert "void attcProcRsp" in UPSTREAM.read_text()
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert removed == ["audio_ble_attc_proc_rsp_4b5448"]
    assert added == ["audio_attc_rsp_error_4b5230", "audio_attc_rsp_find_read_4b52c2",
                     "audio_attc_rsp_find_type_56c3b0", "audio_attc_rsp_mtu_4b527a",
                     "audio_attc_rsp_prepare_write_539dcc", "audio_attc_rsp_read_4b53da",
                     "audio_attc_rsp_read_long_56c454", "audio_attc_rsp_read_multi_var_4b53e2",
                     "audio_attc_rsp_write_4b53dc", "audio_ble_attc_free_pkt_531ac0",
                     "audio_ble_attc_send_req_531144", "audio_ble_attc_setup_req_531160"]
    assert len(prior) == 103 and len(current) == 114
    assert set(removed).issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_BLE_ATTC_PROC_RSP_C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "dependency_source": ref(UPSTREAM),
        "unresolved_before": 103, "unresolved_after": 114,
        "removed_imports": removed, "new_imports": added, "new_providers": removed,
        "remaining_gate": "ATT response dispatch matches bounded stock behavior; twelve child providers, malformed method-17 edge, and final RAM placement remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
