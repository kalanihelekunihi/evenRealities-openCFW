#!/usr/bin/env python3
"""Bind 31 byte-exact stock radio ROM literals into pooled Apollo Main."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-uart-irq-experimental-receipt.json"
PRIOR_RECEIPTS = (G2 / "build/c-firmware/radio-rom-literals-round1036/receipt.json",
                  G2 / "build/c-firmware/radio-rom-tail-round1038/receipt.json")
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BOUND = OUT / "apollo-main-pool-state-radio-literals-bound.o"
RECEIPT = OUT / "pool-state-radio-literals-current-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_UART_IRQ_C_GRAPH"
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    objects = []
    all_entries = {}
    for label, prior_path in zip(("strings", "tail"), PRIOR_RECEIPTS):
        prior = json.loads(prior_path.read_text())
        assert prior["status"] in {"PASS_EXACT_RADIO_ROM_LITERALS_BINDING",
                                   "PASS_EXACT_RADIO_ROM_TAIL_BINDING"}
        source = G2 / prior["source"]
        assert sha(source) == prior["source_sha256"]
        entries = re.findall(
            r"/\* Stock 0x([0-9a-f]+); (\d+) bytes including NUL\. \*/\s*"
            r"const uint8_t ([A-Za-z_][A-Za-z_0-9]*)\[\]", source.read_text())
        assert len(entries) == prior["literal_count"] == (29 if label == "strings" else 2)
        obj = OUT / f"radio-{label}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        with obj.open("rb") as stream:
            elf = ELFFile(stream)
            symbols = {item.name: item for item in elf.get_section_by_name(".symtab").iter_symbols()}
            for addr_text, size_text, name in entries:
                address, size = int(addr_text, 16), int(size_text)
                symbol = symbols[name]
                section = elf.get_section(symbol["st_shndx"])
                actual = section.data()[symbol["st_value"]:symbol["st_value"] + size]
                native = payload[address - 0x438000:address - 0x438000 + size]
                assert section.name == ".rodata" and symbol["st_size"] == size
                assert actual == native and len(native) == size
                assert name not in all_entries
                all_entries[name] = {"address": hex(address), "size": size,
                                     "sha256": hashlib.sha256(actual).hexdigest()}
        objects.append(obj)
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = imports(original)
    assert set(all_entries) <= before and len(all_entries) == 31
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), *map(str, objects),
                    "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - set(all_entries)
    receipt = {
        "status": "PASS_POOLED_MAIN_EXACT_RADIO_ROM_LITERALS_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_receipts": {str(path.relative_to(ROOT)): sha(path) for path in PRIOR_RECEIPTS},
        "stock_payload_sha256": PAYLOAD_SHA,
        "literal_spans": all_entries,
        "pool_abi_objects": {str(path.relative_to(ROOT)): sha(path) for path in objects},
        "imports_resolved": sorted(all_entries),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Relocatable C object does not prove original absolute ROM placement.",
                  "Other Main imports and full image identity remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
