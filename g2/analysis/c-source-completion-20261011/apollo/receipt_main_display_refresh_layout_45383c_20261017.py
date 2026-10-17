#!/usr/bin/env python3
"""Bind checked LVGL refresh layout pass to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-refresh-layout-45383c"
PRIOR = BASE / "main-display-lv-list-insert-before-482b56/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_refresh_layout_45383c.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "refresh-layout.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_REFRESH_LAYOUT_45383C_C"
    assert oracle["cases"] == 256 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = undefined(PRIOR), undefined(CURRENT)
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 108
    assert removed == ["audio_uart_lv_refresh_layout_45383c"] and not added
    record = {
        "status": "PASS_MAIN_DISPLAY_REFRESH_LAYOUT_45383C_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 256,
        "native_body": "0x45383c..0x4539b2", "unresolved_before": 109,
        "unresolved_after": 108, "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Refresh layout matches 256 stock/C fixtures under controlled subtraction, allocation, event, copy and free callees; multi-node initial lists, render pass, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
