#!/usr/bin/env python3
"""Bind checked LVGL draw-layer task body to the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-draw-layer-48895e"
PRIOR = BASE / "main-display-draw-layer-create-48475e/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_lv_draw_layer_48895e.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "draw-layer.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_DISPLAY_DRAW_LAYER_48895E_C"
    assert oracle["cases"] == 64 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 108
    assert removed == ["audio_uart_lv_draw_layer_48895e"] and not added
    assert "audio_uart_lv_draw_layer_48895e" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_DRAW_LAYER_48895E_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 64,
        "native_body": "0x48895e..0x488a38 LVGL layer draw task",
        "unresolved_before": 109, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_draw_layer_48895e"],
        "remaining_gate": "Layer drawing matches stock in 64 controlled cases. Object redraw and other Main imports remain; whole-image source and hardware behavior are open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
