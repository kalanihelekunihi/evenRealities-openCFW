#!/usr/bin/env python3
"""Verify stock frame bytes, C relocations, and Main candidate binding."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from decode_main_low_ram_20261016 import PACKAGE, PAYLOAD_SHA, decode

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016"
HERE = BASE / "main-conversate-anim-frames-20000bf4"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_anim_frames_20000bf4.c"
PRIOR = BASE / "main-conversate-prep-icon-76a47c/candidate.o"
OBJECT = HERE / "frames.o"
CANDIDATE = HERE / "candidate.o"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = PACKAGE.read_bytes()[32:]
    if sha(PACKAGE) == PAYLOAD_SHA or hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("package/payload coordinate mismatch")
    ram = decode()
    stock_table = struct.unpack_from("<6I", ram, 0xbf4)
    if stock_table != tuple(0x76bc00 + 28*i for i in range(6)):
        raise RuntimeError("stock frame table changed")
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {sym.name: sym for sym in elf.get_section_by_name(".symtab").iter_symbols()}
        sections = {
            "pixels": elf.get_section_by_name(".g2_conversate_anim_pixels_6c7930"),
            "descriptors": elf.get_section_by_name(".g2_conversate_anim_descriptors_76bc00"),
            "table": elf.get_section_by_name(".g2_conversate_anim_frames_20000bf4"),
        }
        pixels, descriptors, table = [sections[key].data() for key in ("pixels", "descriptors", "table")]
        if sections["table"]["sh_flags"] & 1 != 1 or \
           sections["descriptors"]["sh_flags"] & 1 or sections["pixels"]["sh_flags"] & 1:
            raise RuntimeError("RAM table or ROM frame section flags changed")
        if pixels != payload[0x6c7930-0x438000:0x6c7930-0x438000+0x960]:
            raise RuntimeError("pixel bytes differ")
        if len(descriptors) != 168 or len(table) != 24:
            raise RuntimeError("C data size changed")
        for i in range(6):
            stock = struct.unpack_from("<7I", payload, 0x76bc00-0x438000+i*28)
            compiled = struct.unpack_from("<7I", descriptors, i*28)
            if compiled[:4] != stock[:4] or compiled[4] != i*0x190 or compiled[5:] != stock[5:]:
                raise RuntimeError(f"descriptor {i} differs")
            if struct.unpack_from("<I", table, i*4)[0] != i*28:
                raise RuntimeError(f"table addend {i} differs")
        for section_name, expected_offset, expected_target in (
            (".rel.g2_conversate_anim_descriptors_76bc00", 16, "audio_conversate_anim_pixels_6c7930"),
            (".rel.g2_conversate_anim_frames_20000bf4", 0, "audio_conversate_anim_descriptors_76bc00"),
        ):
            relocations = elf.get_section_by_name(section_name)
            if relocations is None or len(list(relocations.iter_relocations())) != 6:
                raise RuntimeError(f"missing six relocations in {section_name}")
            symtab = elf.get_section_by_name(".symtab")
            for i, relocation in enumerate(relocations.iter_relocations()):
                if relocation["r_offset"] != expected_offset + i*(28 if expected_offset else 4) or \
                   symtab.get_symbol(relocation["r_info_sym"]).name != expected_target or \
                   relocation["r_info_type"] != 2:
                    raise RuntimeError(f"relocation {i} differs in {section_name}")
        if symbols["audio_conversate_anim_frames_20000bf4"]["st_size"] != 24:
            raise RuntimeError("table symbol extent changed")
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CANDIDATE)], check=True)
    before, after = imports(PRIOR), imports(CANDIDATE)
    if len(before) != 130 or len(after) != 129 or before-after != {"audio_conversate_anim_frames_20000bf4"} or after-before:
        raise RuntimeError("Main import frontier changed")
    record = {"status": "PASS_MAIN_CONVERSATE_ANIM_FRAME_DATA_INTEGRATION",
              "source": ref(SOURCE), "object": ref(OBJECT), "candidate_object": ref(CANDIDATE),
              "prior_candidate": ref(PRIOR), "stock_payload_sha256": PAYLOAD_SHA,
              "decoded_low_ram_sha256": hashlib.sha256(ram).hexdigest(),
              "stock_table": [hex(x) for x in stock_table],
              "stock_descriptor_range": "0x76bc00..0x76bca7",
              "stock_pixel_range": "0x6c7930..0x6c828f",
              "unresolved_before": 130, "unresolved_after": 129,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Other Main imports, exact final placement, whole-image source and hardware behavior remain open."}
    receipt = HERE / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(after), sha(receipt))


if __name__ == "__main__":
    main()
