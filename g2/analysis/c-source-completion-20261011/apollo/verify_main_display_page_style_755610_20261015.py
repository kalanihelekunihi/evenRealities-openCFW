#!/usr/bin/env python3
"""Authenticate the LV font descriptor bytes and relocatable callbacks."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_style_755610.c"
OUT = G2 / "build/c-firmware/20261015/main-display-page-style-755610"
SHIM = '''void audio_uart_lv_font_glyph_dsc_4b26a4(void){}\n
void audio_uart_lv_font_glyph_bitmap_4b239c(void){}\n'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    stock = blob[0x755610-0x438000:0x755634-0x438000]
    if len(stock) != 36 or stock[:8] != bytes.fromhex("a5264b009d234b00") or \
            stock[8:] != bytes.fromhex("00000000100000000300000000ff01001c0078000000000000000000"):
        raise RuntimeError("LV font descriptor changed")
    with tempfile.TemporaryDirectory() as td:
        shim, obj, elf = (Path(td) / name for name in ("shim.c", "style.o", "style.elf"))
        shim.write_text(SHIM)
        common = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                  "-std=c11", "-ffreestanding", "-fno-builtin", "-O2"]
        subprocess.run(common + ["-c", str(SOURCE), "-o", str(obj)], check=True)
        with obj.open("rb") as f:
            ef = ELFFile(f)
            ro = ef.get_section_by_name(".rodata")
            reloc = ef.get_section_by_name(".rel.rodata")
            if ro.data()[8:36] != stock[8:] or ro.data()[:8] != bytes(8) or \
                    [(r["r_offset"], r["r_info_type"]) for r in reloc.iter_relocations()] != \
                    [(0, 2), (4, 2)]:
                raise RuntimeError("C descriptor bytes or callback relocations changed")
        subprocess.run(common + ["-nostdlib", "-Wl,-Ttext=0x100000",
                                 "-Wl,-e,audio_uart_lv_font_glyph_dsc_4b26a4",
                                 str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            ef = ELFFile(f)
            style_addr = syms["audio_uart_display_page_style"]
            for segment in ef.iter_segments():
                if segment["p_type"] == "PT_LOAD" and \
                        segment["p_vaddr"] <= style_addr < segment["p_vaddr"] + segment["p_filesz"]:
                    offset = style_addr - segment["p_vaddr"]
                    compiled = segment.data()[offset:offset+36]
                    break
            else:
                raise RuntimeError("linked C style missing")
        expected_pointers = (syms["audio_uart_lv_font_glyph_dsc_4b26a4"] | 1,
                             syms["audio_uart_lv_font_glyph_bitmap_4b239c"] | 1)
        actual_pointers = (int.from_bytes(compiled[:4], "little"),
                           int.from_bytes(compiled[4:8], "little"))
        if actual_pointers != expected_pointers or compiled[8:] != stock[8:]:
            raise RuntimeError("linked style pointers or descriptor changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_PAGE_STYLE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x755610..0x755633",
               "native_callback_pointers": ["0x4b26a5", "0x4b239d"],
               "descriptor_bytes": 36,
               "limits": ["Descriptor bytes and relocations match; two glyph callback bodies remain imports.",
                          "Runtime LV font use and final image placement remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["descriptor_bytes"])

if __name__ == "__main__": main()
