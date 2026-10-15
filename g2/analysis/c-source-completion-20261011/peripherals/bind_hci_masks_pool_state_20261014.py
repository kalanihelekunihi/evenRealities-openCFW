#!/usr/bin/env python3
"""Bind byte-exact stock HCI command masks to the pooled Apollo Main graph."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-cordio-util-current-receipt.json"
PRIOR_RECEIPT = G2 / "build/c-firmware/ble-hci-reset-masks-round1009/receipt.json"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/ble_hci_reset_masks.c"
OBJECT = OUT / "hci-masks-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-hci-masks-bound.o"
RECEIPT = OUT / "pool-state-hci-masks-current-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    prior = json.loads(PRIOR_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_PINNED_CORDIO_UTIL_C"
    assert prior["status"] == "PASS_BLE_HCI_RESET_MASKS_BINDING"
    assert sha(SOURCE) == prior["source_sha256"]
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    spans = prior["native_spans"]
    assert len(spans) == 3 and all(row["size"] == 8 for row in spans.values())
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    symbols = subprocess.check_output(["arm-none-eabi-nm", "-S", "--radix=x",
                                       str(OBJECT)], text=True)
    contents = subprocess.check_output(["arm-none-eabi-objdump", "-s", "-j", ".rodata",
                                        str(OBJECT)], text=True)
    rodata = bytes.fromhex("".join(re.findall(
        r"(?m)^\s*[0-9a-f]+\s+((?:[0-9a-f]{8}\s*)+)", contents)).replace(" ", ""))
    for name, row in spans.items():
        match = re.search(r"(?m)^([0-9a-f]+)\s+([0-9a-f]+)\s+R\s+" + name + r"$", symbols)
        assert match, name
        offset, size = (int(value, 16) for value in match.groups())
        address = int(row["address"], 16)
        assert size == 8 and rodata[offset:offset+8] == payload[address-0x438000:address-0x438000+8]
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = imports(original)
    assert set(spans) <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(OBJECT),
                    "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - set(spans)
    receipt = {
        "status": "PASS_POOLED_MAIN_EXACT_HCI_MASK_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_receipt": str(PRIOR_RECEIPT.relative_to(ROOT)),
        "prior_receipt_sha256": sha(PRIOR_RECEIPT),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "stock_payload_sha256": PAYLOAD_SHA,
        "stock_spans": spans,
        "pool_abi_object": str(OBJECT.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(OBJECT),
        "imports_resolved": sorted(spans),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Final ROM placement and controller runtime remain open.",
                  "Other Main imports and whole image identity remain unproven."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
