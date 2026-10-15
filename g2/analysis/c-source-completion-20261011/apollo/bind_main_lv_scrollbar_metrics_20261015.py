#!/usr/bin/env python3
"""Bind seven native-compared LV scrollbar metric wrappers to owned style provider."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scrollbar_metrics.c"
STYLE = G2 / "components/audio/uart_thread_source_candidate/display_lv_style_property.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-scrollbar-metrics"
BASE = G2 / "build/c-firmware/20261015/main-lv-scrollbar-descriptor-43e6a6/apollo-main-lv-scrollbar-descriptor-43e6a6.o"
ORACLE = HERE / "verify_main_lv_scrollbar_metrics_oracle_20261015.py"
ADDRESSES = (0x43dd9a, 0x43ddf0, 0x43dde2, 0x43de3e,
             0x43de1c, 0x43de26, 0x43de30)
OWNED = {f"audio_uart_lv_scrollbar_metric_{address:x}" for address in ADDRESSES}
TARGET = "audio_uart_lv_style_property_44bdea"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_scrollbar_metrics.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_METRICS_ORACLE" or
            oracle["cases"] != 42 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("extent metric oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != {TARGET}:
        raise RuntimeError("extent metric object contract changed")
    if TARGET not in symbols(BASE, "--defined-only"):
        raise RuntimeError("source-owned style property missing")
    linked = OUT / "apollo-main-lv-scrollbar-metrics.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before or len(before) != 246 or
            len(after) != 239 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("extent metric linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_METRICS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "existing_style_source": str(STYLE.relative_to(ROOT)),
               "existing_style_source_sha256": sha(STYLE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Seven selector wrappers are source-owned and native-compared; effective opacity and live rendering remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
