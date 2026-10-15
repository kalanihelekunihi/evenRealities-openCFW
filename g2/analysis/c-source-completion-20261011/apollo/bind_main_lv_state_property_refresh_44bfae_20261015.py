#!/usr/bin/env python3
"""Bind native-compared Apollo state property refresh and expose its callbacks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_state_property_refresh_44bfae.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-state-property-refresh-44bfae"
BASE = G2 / "build/c-firmware/20261015/main-lv-transition-style-44c72c/apollo-main-lv-transition-style-44c72c.o"
ORACLE = HERE / "verify_main_lv_state_property_refresh_44bfae_oracle_20261015.py"
OWNED = {"audio_uart_lv_state_property_refresh_44bfae"}
CALLBACKS = {"audio_uart_lv_transition_exec_44cae0",
             "audio_uart_lv_transition_ready_44cc8c",
             "audio_uart_lv_transition_delete_44ccd8"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_state_property_refresh_44bfae.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STATE_PROPERTY_REFRESH_ORACLE" or \
       oracle["cases"] != 6 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("state property refresh oracle changed")
    if symbols(obj, "--defined-only") != OWNED:
        raise RuntimeError("state property object ownership changed")
    base_defined = symbols(BASE, "--defined-only")
    lower = symbols(obj, "-u") - CALLBACKS
    if not lower <= base_defined or symbols(obj, "-u") - base_defined != CALLBACKS:
        raise RuntimeError("state property lower provider changed")
    linked = OUT / "apollo-main-lv-state-property-refresh-44bfae.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before - after != OWNED or after - before != CALLBACKS or \
       len(before) != 234 or len(after) != 236:
        raise RuntimeError("state property linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_STATE_PROPERTY_REFRESH_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 236,
        "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
        "imports_added": sorted(CALLBACKS),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Six controlled cases compare style reads, refresh and animation descriptor setup.",
                   "Three animation callback bodies and the fatal allocation path remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
