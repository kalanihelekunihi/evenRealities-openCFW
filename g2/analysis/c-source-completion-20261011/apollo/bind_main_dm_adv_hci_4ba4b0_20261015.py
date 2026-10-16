#!/usr/bin/env python3
"""Bind legacy advertising HCI handler and three-slot interface table."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_adv_hci_4ba4b0.c"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = G2 / "build/c-firmware/20261015/main-dm-adv-control-extent-34/apollo-main-dm-adv-control-extent-34.o"
OUT = G2 / "build/c-firmware/20261015/main-dm-adv-hci-4ba4b0"
OWNED = {"audio_ble_dm_adv_hci_handler_4ba4b0", "audio_ble_dm_adv_table"}
ADDED = {"audio_ble_dm_adv_gen_conn_complete_4b310a"}
EXISTING = {"audio_ble_dm_adv_control", "audio_ble_dm_handler_state",
            "audio_ble_dm_leg_adv_type_20074fb3", "WsfTimerStartMs", "WsfTimerStop",
            "dmDevPassEvtToDevPriv", "audio_ble_dm_adv_reset_4ba45c",
            "audio_ble_dm_adv_msg_handler_4ba6ac"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def oracle(script, status):
    receipt = json.loads(subprocess.check_output([sys.executable, str(HERE / script)], text=True))
    if receipt["status"] != status or receipt["cases"] != 128:
        raise RuntimeError(f"{script} changed")
    return receipt


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701" or \
            struct.unpack_from("<3I", payload, 0x78a808 - 0x438000) != (0x4ba45d, 0x4ba4b1, 0x4ba6ad):
        raise RuntimeError("native advertising interface changed")
    native = oracle("verify_main_dm_adv_hci_native_20261015.py", "PASS_NATIVE_DM_ADV_HCI")
    bounded = oracle("verify_main_dm_adv_hci_c_20261015.py", "PASS_BOUNDED_DM_ADV_HCI_C")
    if bounded["source_sha256"] != sha(SOURCE):
        raise RuntimeError("advertising HCI source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_dm_adv_hci_4ba4b0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if "audio_ble_dm_adv_table" not in before or OWNED & defined or not EXISTING <= defined or \
            symbols(obj, "--defined-only") != OWNED or \
            symbols(obj, "-u") != EXISTING | ADDED:
        raise RuntimeError("advertising HCI interface symbol frontier changed")
    linked = OUT / "apollo-main-dm-adv-hci-4ba4b0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 192 or len(after) != 192 or \
            before - after != {"audio_ble_dm_adv_table"} or after - before != ADDED:
        raise RuntimeError("advertising HCI interface import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_ADV_HCI_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "native_oracle": native, "c_oracle": bounded,
               "native_interface": "0x78a808", "native_interface_pointers": ["0x4ba45d", "0x4ba4b1", "0x4ba6ad"],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": ["audio_ble_dm_adv_table"], "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["The HCI handler is compared with native logging disabled.",
                          "The directed connection-completion child, diagnostic branches, final image placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
