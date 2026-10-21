#!/usr/bin/env python3
"""Bind documented resident-ROM entry addresses without adding ROM code."""
import argparse
import hashlib
import json
import pathlib
import re
import struct
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[5]
HEADER = ROOT / "g2/src/apollo-bootloader/platform-control/resident_rom_contracts.h"
ENTRIES = {
    "opencfw_boot_rom48": "OPENCFW_BOOT_ROM_INFO_READ_THUMB",
    "opencfw_boot_rom_delay_cycles": "OPENCFW_BOOT_ROM_DELAY_CYCLES_THUMB",
    "opencfw_boot_rom_mram_program": "OPENCFW_BOOT_ROM_MRAM_PROGRAM_THUMB",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path):
    result = subprocess.run(["arm-none-eabi-nm", "-g", str(path)],
                            check=True, capture_output=True, text=True)
    found = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            found[parts[-1]] = (parts[-2], int(parts[0], 16) if len(parts) == 3 else None)
    return found


def executable_sections(path):
    data = path.read_bytes()
    assert data[:6] == b"\x7fELF\x01\x01", "expected little-endian ELF32"
    section_offset = struct.unpack_from("<I", data, 32)[0]
    section_size, count, names_index = struct.unpack_from("<HHH", data, 46)
    assert section_size >= 40 and count and names_index < count
    sections = [struct.unpack_from("<10I", data, section_offset + i * section_size)
                for i in range(count)]
    names_header = sections[names_index]
    names = data[names_header[4]:names_header[4] + names_header[5]]
    result = []
    for section in sections:
        name_offset, kind, flags, _, offset, size, *_ = section
        if kind == 1 and flags & 0x4:
            end = names.find(b"\0", name_offset)
            assert end >= 0
            result.append((names[name_offset:end].decode("ascii"), data[offset:offset + size]))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    assert source.is_file() and source != output
    text = HEADER.read_text()
    values = {}
    for symbol, constant in ENTRIES.items():
        match = re.search(r"\b" + constant + r"\s*=\s*(0x[0-9a-fA-F]+)u\b", text)
        assert match, constant
        values[symbol] = int(match.group(1), 16)
        assert values[symbol] & 1, symbol
    before = symbols(source)
    assert {name for name, (kind, _) in before.items() if kind == "U"} == set(ENTRIES)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = ["arm-none-eabi-ld", "-r"]
    for symbol, address in sorted(values.items()):
        command.extend(["--defsym", f"{symbol}=0x{address:x}"])
    command.extend([str(source), "-o", str(output)])
    subprocess.run(command, check=True)
    after = symbols(output)
    assert not {name for name, (kind, _) in after.items() if kind == "U"}
    assert all(after[symbol] == ("A", address) for symbol, address in values.items())
    before_exec = executable_sections(source)
    after_exec = executable_sections(output)
    assert before_exec == after_exec, "ROM binding changed executable section bytes"
    receipt = {
        "schema": "opencfw-boot-resident-rom-binding-v1",
        "input": str(source.relative_to(ROOT)), "input_sha256": digest(source),
        "output": str(output.relative_to(ROOT)), "output_sha256": digest(output),
        "contract_header": str(HEADER.relative_to(ROOT)), "contract_header_sha256": digest(HEADER),
        "bindings": {symbol: f"0x{address:08x}" for symbol, address in values.items()},
        "input_unresolved": sorted(ENTRIES), "output_unresolved": [],
        "executable_section_bytes_unchanged": True,
        "executable_sections": [{"name": name, "size": len(data),
                                 "sha256": hashlib.sha256(data).hexdigest()}
                                for name, data in before_exec],
        "limits": ["Resident ROM implementations are outside the OTA image.",
                   "Absolute symbol binding does not prove final layout or hardware behavior."],
    }
    result = output.with_suffix(output.suffix + ".receipt.json")
    result.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": receipt["output"], "receipt": str(result.relative_to(ROOT)),
                      "unresolved": 0, "executable_sections_unchanged": True}))


if __name__ == "__main__":
    main()
