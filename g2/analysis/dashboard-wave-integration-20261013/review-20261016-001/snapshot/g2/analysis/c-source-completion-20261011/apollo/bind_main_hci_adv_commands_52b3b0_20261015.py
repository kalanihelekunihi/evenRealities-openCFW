#!/usr/bin/env python3
"""Bind three Cordio legacy advertising HCI providers to Main C."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_adv_commands_52b3b0.c"
BASE = G2 / "build/c-firmware/20261015/main-dm-adv-msg-4ba6ac/apollo-main-dm-adv-msg-4ba6ac.o"
OUT = G2 / "build/c-firmware/20261015/main-hci-adv-commands-52b3b0"
OWNED = {"HciLeSetAdvEnableCmd", "HciLeSetAdvDataCmd", "HciLeSetScanRespDataCmd"}
EXISTING = {"audio_ble_hci_cmd_alloc_52ae38", "audio_ble_hci_cmd_send"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    c_receipt = json.loads(subprocess.check_output(
        [sys.executable, str(HERE / "verify_main_hci_adv_commands_c_20261015.py")], text=True))
    native = json.loads(subprocess.check_output(
        [sys.executable, str(HERE / "verify_main_hci_adv_commands_native_20261015.py")], text=True))
    if c_receipt["status"] != "PASS_BOUNDED_HCI_ADV_COMMANDS_C" or \
            c_receipt["source_sha256"] != sha(SOURCE) or c_receipt["cases"] != 22 or \
            native["status"] != "PASS_NATIVE_HCI_ADV_COMMANDS" or native["cases"] != 22:
        raise RuntimeError("advertising HCI command oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_hci_adv_commands_52b3b0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if not OWNED <= before or OWNED & defined or not EXISTING <= defined or \
            symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != EXISTING:
        raise RuntimeError("advertising HCI provider symbol frontier changed")
    linked = OUT / "apollo-main-hci-adv-commands-52b3b0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 196 or len(after) != 193 or before - after != OWNED or after - before:
        raise RuntimeError("advertising HCI provider import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_HCI_ADV_COMMANDS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "c_oracle": c_receipt, "native_oracle": native,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Advertising data lengths above 31 are guarded in C and outside the native oracle.",
                          "Advertising HCI event handler, configuration child, final placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
