#!/usr/bin/env python3
"""Bind checked LVGL pre-refresh hook to the Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-pre-refresh-454692"
PRIOR = BASE / "main-display-refresh-collect-45377a/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_pre_refresh_454692.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "pre-refresh.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_PRE_REFRESH_454692_C"
    assert oracle["cases"] == 12 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    assert len(prior) == len(current) == 109 and prior == current
    assert "audio_uart_lv_display_pre_refresh_454692" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_PRE_REFRESH_454692_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 12,
        "native_body": "0x454692..0x4546cc", "unresolved_before": 109,
        "unresolved_after": 109, "removed_imports": [], "new_imports": [],
        "new_provider": "audio_uart_lv_display_pre_refresh_454692",
        "remaining_gate": "Pre-refresh hook matches 12 stock/C callback and event cases; layout caller, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
