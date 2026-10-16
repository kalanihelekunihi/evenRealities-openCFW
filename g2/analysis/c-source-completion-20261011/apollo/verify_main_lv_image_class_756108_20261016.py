#!/usr/bin/env python3
"""Verify the source-owned LVGL image class record against stock bytes."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_class_756108.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-class-756108"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
FIELDS = {0: (0x7564f8, "audio_uart_lv_base_class_7564f8"),
          4: (0x498bd1, "audio_uart_lv_image_ctor_498bd0"),
          8: (0x498c6d, "audio_uart_lv_image_dtor_498c6c"),
          12: (0x498c9d, "audio_uart_lv_image_event_498c9c"),
          20: (0x78b33c, "audio_uart_lv_image_class_name_78b33c")}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payload = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PIN
    native = payload[0x756108 - 0x438000:0x75612c - 0x438000]
    if len(native) != 36:
        raise RuntimeError("image class native extent changed")
    for offset, (value, _) in FIELDS.items():
        if struct.unpack_from("<I", native, offset)[0] != value:
            raise RuntimeError(f"image class pointer at {offset} changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display-lv-image-class.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        symbols = {sym.name: sym for sym in symtab.iter_symbols()}
        record = symbols["audio_uart_image_class_756108"]
        section = elf.get_section(record["st_shndx"])
        start = record["st_value"]
        selected = section.data()[start:start + 36]
        if len(selected) != 36 or record["st_size"] != 36:
            raise RuntimeError("C image class extent changed")
        for offset in (16, 24, 28, 32):
            if selected[offset:offset + 4] != native[offset:offset + 4]:
                raise RuntimeError(f"C image class fixed word at {offset} changed")
        reloc = {}
        for sec in elf.iter_sections():
            if sec["sh_type"] != "SHT_REL" or sec["sh_info"] != record["st_shndx"]:
                continue
            for item in sec.iter_relocations():
                offset = item["r_offset"] - start
                if 0 <= offset < 36:
                    reloc[offset] = (symtab.get_symbol(item["r_info_sym"]).name,
                                     item["r_info_type"])
        expected = {offset: (symbol, 2) for offset, (_, symbol) in FIELDS.items()}
        if reloc != expected:
            raise RuntimeError(f"C image class relocations changed: {reloc}")
        name = symbols["audio_uart_lv_image_class_name_78b33c"]
        name_data = elf.get_section(name["st_shndx"]).data()
        selected_name = name_data[name["st_value"]:name["st_value"] + name["st_size"]]
        native_name = payload[0x78b33c - 0x438000:0x78b345 - 0x438000]
        if selected_name != native_name or selected_name != b"lv_image\0":
            raise RuntimeError("C image class name changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_CLASS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "payload_sha256": PIN, "native_span": "0x756108..0x75612b",
              "fixed_words": [16, 24, 28, 32], "relocation_offsets": sorted(FIELDS),
              "limits": ["Image class callback bodies and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
