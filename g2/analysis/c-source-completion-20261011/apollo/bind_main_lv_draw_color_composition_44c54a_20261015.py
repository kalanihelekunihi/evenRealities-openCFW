#!/usr/bin/env python3
"""Bind native-compared Apollo LV color composition into Main."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_composition_44c54a.c"
LEAVES = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_helpers.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-color-composition-44c54a"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-color-helpers/apollo-main-lv-draw-color-helpers.o"
ORACLE = HERE / "verify_main_lv_draw_color_composition_44c54a_oracle_20261015.py"
OWNED = {"audio_uart_lv_draw_color_composite_44c54a",
         "audio_uart_lv_draw_color_chain_44c582"}
LOWER = {"audio_uart_lv_color_blend_482ef6"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_color_composition_44c54a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_COMPOSITION_ORACLE" or
            oracle["cases"] != 54 or oracle["source_sha256"] != sha(SOURCE) or
            oracle["leaf_source_sha256"] != sha(LEAVES)):
        raise RuntimeError("draw color composition oracle changed")
    expected_imports = {"audio_uart_lv_draw_color_style_44b8d0",
                        "audio_uart_lv_draw_color_style_44b8de",
                        "audio_uart_lv_color_with_alpha_440fde",
                        "audio_uart_lv_color_blend_482ef6",
                        "audio_uart_lv_obj_parent_44dca2"}
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != expected_imports:
        raise RuntimeError("draw color composition object contract changed")
    linked = OUT / "apollo-main-lv-draw-color-composition-44c54a.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (after - before != LOWER or before - after or len(before) != 237 or
            len(after) != 238 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("draw color composition linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_COMPOSITION_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "leaf_source": str(LEAVES.relative_to(ROOT)), "leaf_source_sha256": sha(LEAVES),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": sorted(LOWER), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Color composition and ancestor walk are native-compared; true blend provider and full builder remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
