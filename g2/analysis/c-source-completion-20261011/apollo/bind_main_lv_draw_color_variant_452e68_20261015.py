#!/usr/bin/env python3
"""Bind native-compared draw-task conditional color helper into Main."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_variant_452e68.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-color-variant-452e68"
BASE = G2 / "build/c-firmware/20261015/main-lv-color-blend-482ef6/apollo-main-lv-color-blend-482ef6.o"
ORACLE = HERE / "verify_main_lv_draw_color_variant_452e68_oracle_20261015.py"
OWNED = {"audio_uart_lv_draw_color_variant_452e68"}
LOWER = {"audio_uart_lv_draw_color_chain_44c582",
         "audio_uart_lv_draw_color_composite_44c54a",
         "audio_uart_lv_color_with_alpha_440fde",
         "audio_uart_lv_color_blend_482ef6"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_color_variant_452e68.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_VARIANT_ORACLE" or
            oracle["cases"] != 96 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("draw color variant oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != LOWER:
        raise RuntimeError("draw color variant object contract changed")
    linked = OUT / "apollo-main-lv-draw-color-variant-452e68.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before != after or len(after) != 237 or not OWNED <= symbols(linked, "--defined-only"):
        raise RuntimeError("draw color variant linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_VARIANT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Conditional draw color path is native-compared; full builder and renderer remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
