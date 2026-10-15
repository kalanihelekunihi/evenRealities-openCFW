#!/usr/bin/env python3
"""Bind native-compared draw-task opacity providers into Main."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_opacity_452df0.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-opacity-452df0"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-task-init-451b9c/apollo-main-lv-draw-task-init-451b9c.o"
ORACLE = HERE / "verify_main_lv_draw_task_opacity_452df0_oracle_20261015.py"
OWNED = {"audio_uart_lv_draw_task_style_opacity_4525fe",
         "audio_uart_lv_draw_task_opacity_452df0"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_task_opacity_452df0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_OPACITY_ORACLE" or
            oracle["cases"] != 30 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("draw-task opacity oracle changed")
    if (symbols(obj, "--defined-only") != OWNED or
            symbols(obj, "-u") != {"audio_uart_lv_style_property_44bdea",
                                    "audio_uart_lv_effective_opacity_44c47a"}):
        raise RuntimeError("draw-task opacity object contract changed")
    linked = OUT / "apollo-main-lv-draw-task-opacity-452df0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before != after or len(after) != 237 or
            not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("draw-task opacity linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_OPACITY_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Opacity branch and style lookup are native-compared; draw-task builder and renderer remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
