#!/usr/bin/env python3
"""Bind checked LVGL object redraw to the Main C candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-obj-redraw-4531ae"
PRIOR = BASE / "main-display-draw-layer-48895e/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_obj_redraw_4531ae.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "obj-redraw.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_BOUNDED_MAIN_DISPLAY_OBJ_REDRAW_4531AE_C"
    assert oracle["cases"] == 56 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)], check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 109
    assert removed == ["audio_uart_lv_obj_redraw_4531ae"]
    assert added == ["audio_uart_lv_draw_mask_rect_48a98e",
                     "audio_uart_lv_mask_rect_dsc_init_48a984"]
    assert "audio_uart_lv_obj_redraw_4531ae" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_OBJ_REDRAW_4531AE_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 56,
        "native_body": "0x4531ae..0x4534be LVGL object redraw",
        "unresolved_before": 108, "unresolved_after": 109,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_obj_redraw_4531ae"],
        "remaining_gate": "Object redraw matches stock in 56 controlled cases. Two mask helpers and other Main imports remain; whole-image source and hardware behavior are open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
