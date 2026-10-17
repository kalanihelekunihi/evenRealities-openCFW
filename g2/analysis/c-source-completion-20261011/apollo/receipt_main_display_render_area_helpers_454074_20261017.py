#!/usr/bin/env python3
"""Bind checked LVGL render-area and cover-event helper providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-area-helpers-454074"
PRIOR = BASE / "main-display-render-object-chain-453fce/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_area_helpers_454074.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "area-helpers.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
ADDED = ["audio_uart_lv_area_overlap_450f00",
         "audio_uart_lv_obj_adjust_area_440494",
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_AREA_HELPERS_454074_C"
    assert oracle["cases"] == 38 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 111
    assert not removed and added == ADDED
    assert {"audio_uart_lv_render_area_select_454074",
            "audio_uart_lv_render_cover_event_45417c"}.issubset(
                symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_AREA_HELPERS_454074_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 38,
        "native_body": "0x454074..0x454152 plus 0x45417c..0x4541b6",
        "unresolved_before": 108, "unresolved_after": 111,
        "removed_imports": removed, "new_imports": added,
        "new_providers": ["audio_uart_lv_render_area_select_454074",
                          "audio_uart_lv_render_cover_event_45417c"],
        "remaining_gate": "Render-area type and clipping branches plus cover event match stock under controlled lower calls. Draw-object 0x4541b6 and three newly exposed geometry providers, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
