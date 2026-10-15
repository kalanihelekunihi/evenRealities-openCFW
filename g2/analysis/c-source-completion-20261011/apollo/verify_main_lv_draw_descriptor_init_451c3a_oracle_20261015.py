#!/usr/bin/env python3
"""Compare Apollo draw descriptor defaults against the authenticated Main payload."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_descriptor_init_451c3a.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-descriptor-init-451c3a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf = Path(directory) / "init.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_uart_lv_draw_descriptor_init_451c3a", str(SOURCE),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, fill):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            descriptor = 0x20013000
            c.mem_write(descriptor, bytes([fill]) * 0x40)
            c.reg_write(A.UC_ARM_REG_R0, descriptor)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_descriptor_init_451c3a"] if compiled else 0x451c3a
            c.emu_start(start | 1, 0x600000, count=20000)
            return bytes(c.mem_read(descriptor, 0x40))
        suite = (0, 0x55, 0xa5, 0xff)
        for fill in suite:
            native, source = run(False, fill), run(True, fill)
            if native != source: raise AssertionError((fill, native.hex(), source.hex()))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_DESCRIPTOR_INIT_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x451c3a..0x451c6d", "cases": len(suite),
               "compared_bytes_per_case": 0x40,
               "limits": ["Descriptor initialization compared; render queue and live display remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
