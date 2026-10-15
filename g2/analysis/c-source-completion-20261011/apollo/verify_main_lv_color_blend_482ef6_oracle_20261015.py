#!/usr/bin/env python3
"""Compare Apollo RGB and alpha blend directly with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_color_blend_482ef6.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-color-blend-482ef6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
PROVIDERS = (("audio_uart_lv_color_rgb_blend_482e4c", 0x482e4c),
             ("audio_uart_lv_color_blend_482ef6", 0x482ef6))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf = Path(directory) / "blend.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_color_blend_482ef6",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, name, address, foreground, background):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for segment_address, data in segments: c.mem_write(segment_address, data)
            c.mem_map(0x20000000, 0x400000)
            c.reg_write(A.UC_ARM_REG_R0, foreground)
            c.reg_write(A.UC_ARM_REG_R1, background)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            c.emu_start((syms[name] if compiled else address) | 1, 0x600000, count=5000)
            return c.reg_read(A.UC_ARM_REG_R0)
        alpha = (0, 1, 2, 3, 64, 128, 252, 253, 254, 255)
        colors = ((0x112233, 0xaabbcc), (0xffffff, 0x000000),
                  (0x00ff80, 0x8000ff))
        suite = [(name, address, (first << 24) | rgb_first,
                  (second << 24) | rgb_second)
                 for name, address in PROVIDERS
                 for first in alpha for second in alpha
                 for rgb_first, rgb_second in colors]
        for index, (name, address, foreground, background) in enumerate(suite):
            native = run(False, name, address, foreground, background)
            source = run(True, name, address, foreground, background)
            if native != source:
                raise AssertionError((index, name, hex(foreground), hex(background),
                                      hex(native), hex(source)))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_COLOR_BLEND_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x482e4c..0x482f73", "cases": len(suite),
               "limits": ["Pure color functions are directly compared; callers and physical rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
