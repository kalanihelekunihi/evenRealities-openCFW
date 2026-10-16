#!/usr/bin/env python3
"""Check relocated C image assets against authenticated startup and ROM bytes."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_output_style_assets_20261016.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-output-style-assets"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def startup(raw):
    word = lambda a: struct.unpack_from("<I", raw, a - 0x438000)[0]
    record = 0x75d3f4
    pos = record + word(record) - 0x438000
    end = pos + word(record + 4) // 2
    result = bytearray()
    while pos < end:
        token = raw[pos]; pos += 1
        literal = token & 3
        match = token >> 4
        if not literal:
            literal = raw[pos] + 3; pos += 1
        if match == 15:
            match = raw[pos] + 15; pos += 1
        result.extend(raw[pos:pos + literal - 1]); pos += literal - 1
        if match:
            distance = raw[pos]; pos += 1
            high = (token >> 2) & 3
            if high == 3:
                high = raw[pos]; pos += 1
            distance += high << 8
            for _ in range(match + 2):
                result.append(result[-distance])
    assert len(result) == 0x4558
    assert hashlib.sha256(result).hexdigest() == "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"
    return result

def main():
    raw = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(raw).hexdigest() == PIN
    initial = startup(raw)
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "output-style-assets.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    str(SOURCE), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        image = ELFFile(stream)
        symbols = {s.name: s["st_value"] for s in image.get_section_by_name(".symtab").iter_symbols()}
        segments = [(s["p_vaddr"], s.data()) for s in image.iter_segments() if s["p_type"] == "PT_LOAD"]
    def read(address, size):
        for start, data in segments:
            if start <= address and address + size <= start + len(data):
                return data[address - start:address - start + size]
        raise RuntimeError(f"unmapped {address:#x}")
    ram = read(symbols["audio_terminal_output_style_20003f80"], 24)
    assert initial[0x3f98:0x3fa0] != initial[0x3f80:0x3f88]
    for i in range(6):
        stock_descriptor = 0x7733c4 + 28 * i
        startup_pointer = struct.unpack_from("<I", initial, 0x3f80 + 4 * i)[0]
        assert startup_pointer == stock_descriptor
        source_descriptor = symbols[f"terminal_output_descriptor_{i}"]
        assert struct.unpack_from("<I", ram, 4 * i)[0] == source_descriptor
        actual = read(source_descriptor, 28)
        expected = raw[stock_descriptor - 0x438000:stock_descriptor - 0x438000 + 28]
        assert actual[:16] == expected[:16] and actual[20:] == expected[20:]
        stock_pixels = struct.unpack_from("<I", expected, 16)[0]
        source_pixels = symbols[f"terminal_output_pixels_{i}"]
        assert struct.unpack_from("<I", actual, 16)[0] == source_pixels
        assert read(source_pixels, 256) == raw[stock_pixels - 0x438000:stock_pixels - 0x438000 + 256]
    receipt = {"status": "PASS_EXPERIMENTAL_TERMINAL_OUTPUT_STYLE_ASSETS",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "elf_sha256": sha(elf), "descriptors": 6,
               "descriptor_bytes": 168, "pixel_bytes": 1536, "ram_pointer_bytes": 24,
               "startup_sha256": hashlib.sha256(initial).hexdigest(),
               "limits": ["Static initializer and ROM resource bytes only; runtime writes and final address placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sha(path))

if __name__ == "__main__":
    main()
