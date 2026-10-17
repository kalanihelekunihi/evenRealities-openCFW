#!/usr/bin/env python3
"""Bind checked LVGL mask task constructor to the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-draw-mask-rect-48a98e"
PRIOR = BASE / "main-display-mask-rect-dsc-init-48a984/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_draw_mask_rect_48a98e.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "mask-draw.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_DISPLAY_DRAW_MASK_RECT_48A98E_C"
    assert oracle["cases"] == 32 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 107
    assert removed == ["audio_uart_lv_draw_mask_rect_48a98e"] and not added
    assert "audio_uart_lv_draw_mask_rect_48a98e" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_DRAW_MASK_RECT_48A98E_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 32,
        "native_body": "0x48a98e..0x48aa38 LVGL mask rectangle task",
        "unresolved_before": 108, "unresolved_after": 107,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_draw_mask_rect_48a98e"],
        "remaining_gate": "Mask rectangle task matches stock in 32 controlled cases. The draw-object dependency chain is now internally linked; other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
