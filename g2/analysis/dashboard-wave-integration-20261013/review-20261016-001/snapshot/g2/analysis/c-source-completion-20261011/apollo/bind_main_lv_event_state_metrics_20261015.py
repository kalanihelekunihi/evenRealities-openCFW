#!/usr/bin/env python3
"""Bind ten native-compared LV event-state metric wrappers to owned style provider."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_state_metrics.c"
STYLE = G2 / "components/audio/uart_thread_source_candidate/display_lv_style_property.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-state-metrics"
BASE = G2 / "build/c-firmware/20261015/main-lv-event-layer-451960/apollo-main-lv-event-layer-451960.o"
ORACLE = HERE / "verify_main_lv_event_state_metrics_oracle_20261015.py"
ADDRESSES = (0x43de4a, 0x43dd72, 0x43dd7c, 0x43ddd8, 0x43dda8,
             0x43de6a, 0x43ddb4, 0x43ddcc, 0x43ddc0, 0x43de54)
OWNED = {f"audio_uart_lv_event_state_metric_{address:x}" for address in ADDRESSES}
TARGET = "audio_uart_lv_style_property_44bdea"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_event_state_metrics.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_METRICS_ORACLE" or
            oracle["cases"] != 60 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("extent metric oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != {TARGET}:
        raise RuntimeError("extent metric object contract changed")
    if TARGET not in symbols(BASE, "--defined-only"):
        raise RuntimeError("source-owned style property missing")
    linked = OUT / "apollo-main-lv-event-state-metrics.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before != after or len(before) != 236 or len(after) != 236 or
            OWNED & symbols(BASE, "--defined-only") or
            not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("extent metric linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_METRICS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "existing_style_source": str(STYLE.relative_to(ROOT)),
               "existing_style_source_sha256": sha(STYLE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Ten selector wrappers are source-owned ahead of the event-state parent body; live event and theme effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
