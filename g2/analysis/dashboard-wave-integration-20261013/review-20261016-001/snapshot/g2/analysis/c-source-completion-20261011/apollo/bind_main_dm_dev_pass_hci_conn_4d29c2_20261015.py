#!/usr/bin/env python3
"""Bind dynamic connection interface callback forwarding to Main C."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_dev_pass_hci_conn_4d29c2.c"
BASE = G2 / "build/c-firmware/20261015/main-dm-adv-gen-conn-4b310a/apollo-main-dm-adv-gen-conn-4b310a.o"
OUT = G2 / "build/c-firmware/20261015/main-dm-dev-pass-hci-conn-4d29c2"
OWNED = {"audio_ble_dm_dev_pass_hci_conn_4d29c2"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def oracle(script, status):
    receipt = json.loads(subprocess.check_output([sys.executable, str(HERE / script)], text=True))
    if receipt["status"] != status or receipt["cases"] != 16:
        raise RuntimeError(f"{script} changed")
    return receipt


def main():
    native = oracle("verify_main_dm_dev_pass_hci_conn_native_20261015.py", "PASS_NATIVE_DM_DEV_PASS_HCI_CONN")
    bounded = oracle("verify_main_dm_dev_pass_hci_conn_c_20261015.py", "PASS_BOUNDED_DM_DEV_PASS_HCI_CONN_C")
    if bounded["source_sha256"] != sha(SOURCE):
        raise RuntimeError("connection callback bridge source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ble_dm_dev_pass_hci_conn_4d29c2.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if not OWNED <= before or OWNED & defined or "audio_ble_dm_config" not in defined or \
            symbols(obj, "--defined-only") != OWNED or \
            symbols(obj, "-u") != {"audio_ble_dm_config"}:
        raise RuntimeError("connection callback bridge symbol frontier changed")
    linked = OUT / "apollo-main-dm-dev-pass-hci-conn-4d29c2.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 192 or len(after) != 191 or before - after != OWNED or after - before:
        raise RuntimeError("connection callback bridge import delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_DEV_PASS_HCI_CONN_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "source_owned_symbols": sorted(OWNED),
               "native_oracle": native, "c_oracle": bounded,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Dynamic callback routing is bounded to an initialized connection interface.",
                          "Final interface installation, image placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
