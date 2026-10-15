#!/usr/bin/env python3
"""Bind area copy and two style children ahead of event-state parent."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_state_small_helpers.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-state-small-helpers"
BASE = G2 / "build/c-firmware/20261015/main-lv-event-state-metrics/apollo-main-lv-event-state-metrics.o"
ORACLE = HERE / "verify_main_lv_event_state_small_helpers_oracle_20261015.py"
OWNED = {"audio_uart_lv_event_area_copy_43dcc0",
         "audio_uart_lv_event_state_metric_43de06",
         "audio_uart_lv_event_state_metric_43ddfc"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_event_state_small_helpers.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_SMALL_HELPERS_ORACLE" or
            oracle["cases"] != 22 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("event-state small helper oracle changed")
    if (symbols(obj, "--defined-only") != OWNED or
            symbols(obj, "-u") != {"audio_uart_lv_style_property_44bdea"}):
        raise RuntimeError("event-state small helper object contract changed")
    linked = OUT / "apollo-main-lv-event-state-small-helpers.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before != after or len(before) != 236 or len(after) != 236 or
            OWNED & symbols(BASE, "--defined-only") or
            not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("event-state small helper linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_SMALL_HELPERS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": [],
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Area copy and two style wrappers are source-owned ahead of event-state parent; live draw effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
