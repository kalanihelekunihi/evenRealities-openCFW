#!/usr/bin/env python3
"""Bind native-compared Apollo draw-task builder into Main."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_build_452616.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-build-452616"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-rgb-mix-452e22/apollo-main-lv-draw-rgb-mix-452e22.o"
ORACLE = HERE / "verify_main_lv_draw_task_build_452616_oracle_20261015.py"
OWNED = {"audio_uart_lv_draw_task_build_452616"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_task_build_452616.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_BUILD_ORACLE" or
            oracle["cases"] != 30 or oracle["controlled_provider_count"] != 37 or
            oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("draw-task builder oracle changed")
    lower = symbols(obj, "-u")
    if symbols(obj, "--defined-only") != OWNED or len(lower) != 37:
        raise RuntimeError("draw-task builder object contract changed")
    defined_base = symbols(BASE, "--defined-only")
    if not lower <= defined_base:
        raise RuntimeError(("draw-task builder lower providers absent", sorted(lower - defined_base)))
    linked = OUT / "apollo-main-lv-draw-task-build-452616.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before or len(before) != 237 or
            len(after) != 236 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("draw-task builder linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_BUILD_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Builder task memory and controlled provider calls are native-compared; live style mutation, renderer and physical display remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
