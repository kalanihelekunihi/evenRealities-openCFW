#!/usr/bin/env python3
"""Bind stock-checked render-area spelling of the existing 0x440494 owner."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-area-adjust-alias-440494"
PRIOR = BASE / "main-display-render-geometry-leaf-450f00/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_area_adjust_alias_440494.c"
OWNER = ROOT / "g2/components/audio/uart_thread_source_candidate/display_lv_scrollbar_clip.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "alias.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_AREA_ADJUST_ALIAS_440494_C"
    assert oracle["cases"] == 128 and oracle["source_sha256"] == sha(SOURCE)
    assert oracle["owner_source_sha256"] == sha(OWNER)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 108
    assert removed == ["audio_uart_lv_obj_adjust_area_440494"] and not added
    assert "audio_uart_lv_object_scrollbar_area_440494" in symbols(PRIOR, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_AREA_ADJUST_ALIAS_440494_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "owner_source": ref(OWNER),
        "oracle": ref(ORACLE), "oracle_cases": 128,
        "native_body": "0x440494..0x4405d4 via existing 0x4403e6 owner",
        "unresolved_before": 109, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Area-adjust alias and existing C owner match stock under controlled parent/clip calls. Draw-object 0x4541b6, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
