#!/usr/bin/env python3
"""Bind native-compared Apollo draw-task style selectors into Main."""
import hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_metrics.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-metrics"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-task-opacity-452df0/apollo-main-lv-draw-task-opacity-452df0.o"
ORACLE = HERE / "verify_main_lv_draw_task_metrics_oracle_20261015.py"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    owned = {f"audio_uart_lv_draw_metric_{address}" for address in
             re.findall(r"^(?:RAW|BYTE|BOOL)\(([0-9a-f]{6}),", SOURCE.read_text(), re.M)}
    if len(owned) != 43: raise RuntimeError("draw-task metric inventory changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_task_metrics.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_METRICS_ORACLE" or
            oracle["cases"] != 215 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("draw-task metric oracle changed")
    if (symbols(obj, "--defined-only") != owned or
            symbols(obj, "-u") != {"audio_uart_lv_style_property_44bdea"}):
        raise RuntimeError("draw-task metric object contract changed")
    linked = OUT / "apollo-main-lv-draw-task-metrics.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before != after or len(after) != 237 or not owned <= symbols(linked, "--defined-only"):
        raise RuntimeError("draw-task metric linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_METRICS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(owned), "imports_resolved": [],
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["43 selectors are native-compared with controlled style property results; builder and renderer remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(owned), len(before), len(after), sha(path))

if __name__ == "__main__": main()
