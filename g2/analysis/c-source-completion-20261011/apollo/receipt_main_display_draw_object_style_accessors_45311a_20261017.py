#!/usr/bin/env python3
"""Bind checked draw-object style and color-format leaf providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-draw-object-style-accessors-45311a"
PRIOR = BASE / "main-display-render-area-adjust-alias-440494/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_draw_object_style_accessors_45311a.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "style-accessors.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
ADDRESSES = (0x45311a, 0x453124, 0x45312e, 0x453138, 0x453142,
             0x45314c, 0x453156, 0x453160, 0x45316a, 0x453180,
             0x45318c, 0x453198, 0x4531a4)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_DRAW_OBJECT_STYLE_ACCESSORS_45311A_C"
    assert oracle["cases"] == 224 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 108
    assert not removed and not added
    expected = {f"audio_uart_lv_draw_style_metric_{address:x}" for address in ADDRESSES}
    expected.add("audio_uart_lv_color_format_bytes_441004")
    assert expected.issubset(symbols(CURRENT, "--defined-only"))
    record = {
        "status": "PASS_MAIN_DISPLAY_DRAW_OBJECT_STYLE_ACCESSORS_45311A_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 224,
        "native_body": "0x45311a..0x4531ae property wrappers plus 0x441004..0x441016",
        "unresolved_before": 108, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "new_providers": sorted(expected),
        "remaining_gate": "Fourteen draw-object style/color leaf providers match stock under controlled lower calls. Draw-object 0x4541b6 task assembly, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
