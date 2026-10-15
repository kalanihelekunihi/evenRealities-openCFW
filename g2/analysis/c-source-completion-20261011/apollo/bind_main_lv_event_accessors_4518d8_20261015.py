#!/usr/bin/env python3
"""Bind native-compared LV input-device and key event accessors."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_accessors_4518d8.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-accessors-4518d8"
BASE = G2 / "build/c-firmware/20261015/main-lv-base-class-7564f8/apollo-main-lv-base-class-7564f8.o"
ORACLE = HERE / "verify_main_lv_event_accessors_4518d8_oracle_20261015.py"
OWNED = {"audio_uart_lv_input_reset_4518d8", "audio_uart_lv_event_param_4519a0"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_event_accessors_4518d8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_ACCESSORS_ORACLE" or
            oracle["cases"] != 38 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("event accessor oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != {"audio_uart_lvgl_log"}:
        raise RuntimeError("event accessor object contract changed")
    linked = OUT / "apollo-main-lv-event-accessors-4518d8.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before or len(before) != 241 or len(after) != 239 or
            not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("event accessor linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_ACCESSORS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Input-device and key accessors have controlled native-compared C bodies; live input state remains open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
