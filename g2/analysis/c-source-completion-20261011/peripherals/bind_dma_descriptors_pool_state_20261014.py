#!/usr/bin/env python3
"""Bind twelve stock-matched DMA descriptor rows to pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-dm-hci-route-current-receipt.json"
PROVIDER_RECEIPT = G2 / "analysis/c-source-completion-20261011/peripherals/root-dma-descriptors-round433/dma-descriptors-receipt.json"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-dma-descriptors-round433/dma_descriptors.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = OUT / "dma-descriptors-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-dma-descriptors-bound.o"
RECEIPT = OUT / "pool-state-dma-descriptors-current-receipt.json"
PROVIDER = "audio_ble_dma_channels_rom_6c0f40"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_EXACT_DM_HCI_ROUTE_C"
    assert provider["status"] == "completed"
    assert provider["import_delta"]["removed"] == [PROVIDER]
    evidence = provider["native_evidence"]
    assert evidence["row_count"] == 12 and evidence["row_bytes"] == 40
    assert evidence["compiled_symbol_size"] == 480
    assert sha(SOURCE) == provider["source_unit"]["source_sha256"]
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbol, = [item for item in elf.get_section_by_name(".symtab").iter_symbols()
                   if item.name == PROVIDER]
        assert symbol["st_size"] == 480
        section = elf.get_section(symbol["st_shndx"])
        actual = section.data()[symbol["st_value"]:symbol["st_value"] + 480]
        native = payload[0x6c0f40 - 0x438000:0x6c0f40 - 0x438000 + 480]
        assert len(actual) == 480 and actual == native
        assert hashlib.sha256(actual).hexdigest() == evidence["full_table_sha256"]
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = imports(original)
    assert PROVIDER in before
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(OBJECT),
                    "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {PROVIDER}
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_DMA_DESCRIPTOR_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
        "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "stock_payload_sha256": PAYLOAD_SHA,
        "table_start": "0x6c0f40",
        "row_count": 12,
        "row_bytes": 40,
        "matched_bytes": 480,
        "table_sha256": hashlib.sha256(actual).hexdigest(),
        "pool_abi_object": str(OBJECT.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(OBJECT),
        "imports_resolved": [PROVIDER],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Only twelve indexed rows are exact; original allocation beyond them is not established.",
                  "Final ROM placement, DMA hardware behavior and other Main imports remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
