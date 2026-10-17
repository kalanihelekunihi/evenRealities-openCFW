#!/usr/bin/env python3
"""Bind checked LVGL refresh-area coalescing to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-refresh-collect-45377a"
PRIOR = BASE / "main-display-refresh-timer-45360c/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_refresh_collect_45377a.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "refresh-collect.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def undefined(path):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_REFRESH_COLLECT_45377A_C"
    assert oracle["cases"] == 300 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 110 and len(current) == 109
    assert removed == ["audio_uart_lv_refresh_collect_45377a"] and not added
    record = {
        "status": "PASS_MAIN_DISPLAY_REFRESH_COLLECT_45377A_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 300,
        "native_body": "0x45377a..0x453838", "unresolved_before": len(prior),
        "unresolved_after": len(current), "removed_imports": removed,
        "new_imports": added,
        "remaining_gate": "Refresh-area coalescing matches 300 stock/C cases; layout/render passes, remaining Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
