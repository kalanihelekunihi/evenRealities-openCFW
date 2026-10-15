#!/usr/bin/env python3
"""Bind exact stock HCI event-size bytes into the current Main C pool."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-interrupt-mask-current-receipt.json"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-event-sizes-round427/event_sizes.c"
PROVIDER = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-event-sizes-round427/event-size-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = OUT / "hci-event-sizes-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-hci-event-sizes-bound.o"
RECEIPT = OUT / "pool-state-hci-event-sizes-current-receipt.json"
NAME = "audio_ble_hci_event_sizes_6e3720"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    provider = json.loads(PROVIDER.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_EXACT_AMBIQ_INTERRUPT_MASK_C"
    assert provider["status"] == "PASS_EXPERIMENTAL_HCI_EVENT_SIZE_CANDIDATE"
    assert provider["removed_imports"] == [NAME]
    assert provider["source"]["sha256"] == sha(SOURCE)
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbol, = [s for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name == NAME]
        assert symbol["st_size"] == 86
        section = elf.get_section(symbol["st_shndx"])
        assert section.name == ".rodata"
        actual = section.data()[symbol["st_value"]:symbol["st_value"] + 86]
    offset = 0x6e3720 - 0x438000
    assert actual == payload[offset:offset + 86]
    before = imports(prior)
    assert NAME in before and not imports(OBJECT)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {NAME}
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_EVENT_SIZE_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "provider_receipt": str(PROVIDER.relative_to(ROOT)), "provider_receipt_sha256": sha(PROVIDER),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "stock_payload_sha256": hashlib.sha256(payload).hexdigest(),
               "table_start": "0x6e3720", "matched_bytes": 86,
               "table_sha256": hashlib.sha256(actual).hexdigest(),
               "pool_abi_object": str(OBJECT.relative_to(ROOT)), "pool_abi_object_sha256": sha(OBJECT),
               "imports_resolved": [NAME], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["The index-85 byte is exact ROM data, but original table allocation extent remains unproved.",
                         "Other Main imports, final placement, and controller behavior remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
