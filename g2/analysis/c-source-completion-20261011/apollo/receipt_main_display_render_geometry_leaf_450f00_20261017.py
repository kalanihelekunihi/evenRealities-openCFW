#!/usr/bin/env python3
"""Bind checked LVGL overlap and extra-draw-size leaf providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-geometry-leaf-450f00"
PRIOR = BASE / "main-display-render-area-helpers-454074/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_geometry_leaf_450f00.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "geometry-leaf.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
REMOVED = ["audio_uart_lv_area_overlap_450f00",
           "audio_uart_lv_obj_ext_draw_size_452dc8"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_GEOMETRY_LEAF_450F00_C"
    assert oracle["cases"] == 157 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 111 and len(current) == 109
    assert removed == REMOVED and not added
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_GEOMETRY_LEAF_450F00_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 157,
        "native_body": "0x450f00..0x450f28 plus 0x452dc8..0x452dd8",
        "unresolved_before": 111, "unresolved_after": 109,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Area overlap and extra draw-size getter match direct stock instructions. Area adjust transform 0x440494, draw-object 0x4541b6, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
