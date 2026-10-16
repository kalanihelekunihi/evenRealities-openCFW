#!/usr/bin/env python3
"""Compare the source-owned logger nanopb graph with official Main data."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_logger_ble_pb_descriptor_777da4.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
OUT = G2 / "build/c-firmware/20261015/main-logger-ble-pb-descriptor-777da4"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as temp:
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_ble_log_pb_descriptor_777da4", str(SOURCE),
                    "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def read(compiled, address, size):
        if not compiled:
            return IMAGE[address-0x438000:address-0x438000+size]
        for base, data in segments:
            if base <= address and address+size <= base+len(data):
                return data[address-base:address-base+size]
        raise AssertionError((hex(address), size))

    def word(compiled, address): return struct.unpack("<I", read(compiled, address, 4))[0]

    def graph(compiled, root):
        def desc(address, field_words, children):
            data = read(compiled, address, 24)
            fields, sub, default, callback, count, required, largest, pad = \
                struct.unpack("<4I4H", data)
            result = (tuple(word(compiled, fields+4*i) for i in range(field_words)),
                      (default, callback, count, required, largest, pad))
            child_addresses = tuple(word(compiled, sub+4*i) for i in range(children+1))
            assert child_addresses[-1] == 0
            return result, child_addresses[:-1]

        top, children = desc(root, 15, 3)
        leaves = tuple(desc(child, 2 if i == 0 else 3, 0)[0]
                       for i, child in enumerate(children))
        return top, leaves

    native = graph(False, 0x777da4)
    candidate = graph(True, symbols["audio_uart_ble_log_pb_descriptor_777da4"])
    if native != candidate:
        raise AssertionError((native, candidate))
    receipt = {"status": "PASS_NATIVE_MAIN_LOGGER_BLE_PB_DESCRIPTOR_777DA4",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_root_sha256": hashlib.sha256(read(False, 0x777da4, 24)).hexdigest(),
               "native_root": "0x777da4", "source_owned_symbols":
               ["audio_uart_ble_log_pb_descriptor_777da4"],
               "compared_descriptors": 4, "compared_field_words": 23,
               "limits": ["Graph bytes and edges were compared; final placement and hardware encode behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], hashlib.sha256(path.read_bytes()).hexdigest())
