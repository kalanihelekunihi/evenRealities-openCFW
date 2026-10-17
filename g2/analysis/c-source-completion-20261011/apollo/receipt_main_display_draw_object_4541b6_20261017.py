#!/usr/bin/env python3
"""Bind the stock-compared LVGL refr_obj body to the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-draw-object-4541b6"
PRIOR = BASE / "main-display-draw-object-style-accessors-45311a/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_draw_object_4541b6.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-direct-receipt.json", HERE / "draw-object.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_DISPLAY_DRAW_OBJECT_4541B6_C"
    assert oracle["cases"] == 15 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 110
    assert removed == ["audio_uart_lv_draw_object_4541b6"]
    assert added == ["audio_uart_lv_draw_layer_48895e",
                     "audio_uart_lv_draw_layer_create_48475e",
                     "audio_uart_lv_obj_redraw_4531ae"]
    assert "audio_uart_lv_draw_object_4541b6" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_DRAW_OBJECT_4541B6_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 15,
        "native_body": "0x4541b6..0x4544ae LVGL refr_obj",
        "unresolved_before": 108, "unresolved_after": 110,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_draw_object_4541b6"],
        "remaining_gate": "Draw-object direct and tiled branches match stock in 15 controlled cases. Three new layer/redraw imports and other Main imports remain; whole-image source and hardware behavior are open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
