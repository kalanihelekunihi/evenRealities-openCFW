#!/usr/bin/env python3
"""Bind controlled native-compared Apollo render-task evaluator."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_render_task_evaluate_48458e.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-render-task-evaluate-48458e"
BASE = G2 / "build/c-firmware/20261015/main-lv-refresh-tasks-484548/apollo-main-lv-refresh-tasks-484548.o"
ORACLE = HERE / "verify_main_lv_render_task_evaluate_48458e_oracle_20261015.py"
OWNED = {"audio_uart_lv_render_task_evaluate_48458e"}
ADDED = {"audio_uart_lv_render_task_free_4848e8"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_render_task_evaluate_48458e.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_EVALUATE_ORACLE" or
            oracle["cases"] != 36 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("render task evaluator oracle changed")
    lower = symbols(obj, "-u")
    if symbols(obj, "--defined-only") != OWNED or lower != {
            "audio_uart_lv_draw_dispatch_request_48462e", *ADDED}:
        raise RuntimeError("render task evaluator object contract changed")
    if not lower - ADDED <= symbols(BASE, "--defined-only"):
        raise RuntimeError("render task evaluator lower provider absent")
    linked = OUT / "apollo-main-lv-render-task-evaluate-48458e.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before != ADDED or
            len(before) != 237 or len(after) != 237):
        raise RuntimeError("render task evaluator linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_EVALUATE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 237, "unresolved_after": 237,
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Evaluator control flow is compared with controlled free and backend callbacks; task-free body remains open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
