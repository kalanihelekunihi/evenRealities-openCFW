#!/usr/bin/env python3
"""Bind controlled native-compared Apollo render-task queue finalizer."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_render_task_queue_484476.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-render-task-queue-484476"
BASE = G2 / "build/c-firmware/20261015/main-lv-render-task-alloc-4843ee/apollo-main-lv-render-task-alloc-4843ee.o"
ORACLE = HERE / "verify_main_lv_render_task_queue_484476_oracle_20261015.py"
OWNED = {"audio_uart_lv_render_task_queue_484476"}
ADDED = {"audio_uart_lv_refresh_tasks_484548"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_render_task_queue_484476.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_QUEUE_ORACLE" or
            oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("render task queue oracle changed")
    lower = symbols(obj, "-u")
    if symbols(obj, "--defined-only") != OWNED or lower != {
            "audio_uart_lv_obj_event_451670", "audio_uart_lv_obj_has_flag_43e0e0",
            "audio_uart_lvgl_log", *ADDED}:
        raise RuntimeError("render task queue object contract changed")
    if not lower - ADDED <= symbols(BASE, "--defined-only"):
        raise RuntimeError("render task queue lower provider absent")
    linked = OUT / "apollo-main-lv-render-task-queue-484476.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if after - before != ADDED or before - after or len(before) != 236 or len(after) != 237:
        raise RuntimeError("render task queue linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_QUEUE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 236, "unresolved_after": 237,
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": sorted(ADDED), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Queue logic is compared with controlled callbacks; live refresh and logger effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
