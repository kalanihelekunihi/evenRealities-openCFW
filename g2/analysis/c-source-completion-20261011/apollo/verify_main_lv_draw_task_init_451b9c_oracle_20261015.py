#!/usr/bin/env python3
"""Compare the 0x70-byte LV draw-task initialization with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_init_451b9c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-init-451b9c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf = Path(directory) / "init.elf"
        stub = Path(directory) / "style.c"
        stub.write_text("const unsigned char audio_uart_display_page_style[36] = {0};\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_task_init_451b9c",
                        str(SOURCE), str(stub), "-o", str(elf)], check=True)
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
            task = 0x20013000
            c.mem_write(task, bytes([fill]) * 0x80)
            c.reg_write(A.UC_ARM_REG_R0, task)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_task_init_451b9c"] if compiled else 0x451b9c
            c.emu_start(start | 1, 0x600000, count=20000)
            data = bytearray(c.mem_read(task, 0x80))
            style = syms["audio_uart_display_page_style"] if compiled else 0x755610
            if int.from_bytes(data[0x34:0x38], "little") != style:
                raise AssertionError(("style pointer", compiled, fill, data[0x34:0x38].hex(), hex(style)))
            data[0x34:0x38] = b"STYL"
            return c.reg_read(A.UC_ARM_REG_R0), bytes(data)
        suite = (0, 0x55, 0xa5, 0xff)
        for fill in suite:
            native, source = run(False, fill), run(True, fill)
            if native != source: raise AssertionError((fill, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_INIT_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x451b9c..0x451c39", "cases": len(suite),
               "compared_bytes_per_case": 0x80,
               "limits": ["Stock helper calls were executed; class pointer was normalized to its source-owned relocation. Rendering remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
