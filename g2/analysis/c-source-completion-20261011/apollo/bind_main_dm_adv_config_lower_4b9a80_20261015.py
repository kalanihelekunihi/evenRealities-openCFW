#!/usr/bin/env python3
"""Bind the legacy advertising configuration child and parameter command."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_adv_config_lower_4b9a80.c"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = G2 / "build/c-firmware/20261015/main-hci-adv-commands-52b3b0/apollo-main-hci-adv-commands-52b3b0.o"
OUT = G2 / "build/c-firmware/20261015/main-dm-adv-config-lower-4b9a80"
OWNED = {"audio_ble_dm_adv_config_lower_4b9a80", "audio_ble_dm_ll_addr_type_4d2a84",
         "HciLeSetAdvParamCmd", "audio_ble_dm_leg_adv_type_20074fb3"}
EXISTING = {"audio_ble_dm_adv_control", "audio_ble_dm_handler_state",
            "audio_ble_hci_cmd_alloc_52ae38", "audio_ble_hci_cmd_send"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def oracle(script, status):
    receipt = json.loads(subprocess.check_output([sys.executable, str(HERE / script)], text=True))
    if receipt["status"] != status or receipt["cases"] != 20:
        raise RuntimeError(f"{script} changed")
    return receipt


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701" or \
            struct.unpack_from("<I", payload, 0x4ba6c0 - 0x438000)[0] != 0x20074fb3:
        raise RuntimeError("advertising leg type native pointer changed")
    native = oracle("verify_main_dm_adv_config_native_20261015.py", "PASS_NATIVE_DM_ADV_CONFIG")
    bounded = oracle("verify_main_dm_adv_config_c_20261015.py", "PASS_BOUNDED_DM_ADV_CONFIG_C")
    if bounded["source_sha256"] != sha(SOURCE):
        raise RuntimeError("advertising configuration source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_dm_adv_config_lower_4b9a80.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if "audio_ble_dm_adv_config_lower_4b9a80" not in before or \
            OWNED & defined or not EXISTING <= defined or \
            symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != EXISTING:
        raise RuntimeError("advertising configuration symbol frontier changed")
    linked = OUT / "apollo-main-dm-adv-config-lower-4b9a80.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    resolved = {"audio_ble_dm_adv_config_lower_4b9a80"}
    if len(before) != 193 or len(after) != 192 or before - after != resolved or after - before:
        raise RuntimeError("advertising configuration import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_ADV_CONFIG_LOWER_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "native_oracle": native, "c_oracle": bounded,
               "leg_type_native_cell": "0x20074fb3", "leg_type_source_bytes": 1,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(resolved), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Configuration and command behavior are bounded to the compared inputs.",
                          "Advertising HCI event handler, leg type startup contents, final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
