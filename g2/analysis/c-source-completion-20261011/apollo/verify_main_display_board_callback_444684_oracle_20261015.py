#!/usr/bin/env python3
"""Compare stock board callback dispatch with its compiled C provider."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_board_callback_444684.c"
OUT = G2 / "build/c-firmware/20261015/main-display-board-callback-444684"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def word(cpu, address): return int.from_bytes(cpu.mem_read(address, 4), "little")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if hashlib.sha256(blob[0x444684-0x438000:0x444690-0x438000]).hexdigest() != \
            "01a92609fa69e1f57bc32b2314f6c09dadb9f9ab80ae8a49c85f847248edffb7":
        raise RuntimeError("board callback span changed")
    for address, value in ((0x4448b8, 0x200742f0), (0x4448bc, 0x444685)):
        if int.from_bytes(blob[address-0x438000:address-0x438000+4], "little") != value:
            raise RuntimeError("board callback literal changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "oracle.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_board_callback_444684",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, ignored, value):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for addr, data in segments: cpu.mem_write(addr, data)
            cpu.mem_map(0x20000000, 0x400000)
            cell = (syms["audio_uart_stdio_print_char_cell_200742f0"]
                    if compiled else 0x200742f0)
            cpu.mem_write(cell, (0x20015001).to_bytes(4, "little"))
            cpu.mem_write(0x20015000, bytes.fromhex("7047"))
            trace = []
            def hook(cpu, address, size, _):
                if address != 0x20015000: return
                trace.append(cpu.reg_read(A.UC_ARM_REG_R0))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, ignored)
            cpu.reg_write(A.UC_ARM_REG_R1, value)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            cpu.emu_start((syms["audio_uart_display_board_callback_444684"]
                           if compiled else 0x444684) | 1, 0x600000, count=10000)
            pointer = (word(cpu, syms["audio_uart_display_board_data"])
                       if compiled else int.from_bytes(blob[0x4448bc-0x438000:0x4448c0-0x438000], "little"))
            return trace, pointer
        values = (0, 1, 0x12345678, 0x80000000, 0xffffffff)
        cases = [(a, b) for a in values for b in values]
        for ignored, value in cases:
            stock_trace, stock_ptr = run(False, ignored, value)
            source_trace, source_ptr = run(True, ignored, value)
            if stock_trace != source_trace or stock_ptr != 0x444685 or \
                    source_ptr != (syms["audio_uart_display_board_callback_444684"] | 1):
                raise AssertionError((ignored, value, stock_trace, source_trace,
                                      hex(stock_ptr), hex(source_ptr)))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_BOARD_CALLBACK_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_span": "0x444684..0x44468f", "native_pointer_word": "0x4448bc",
               "native_target_cell": "0x200742f0", "cases": len(cases),
               "limits": ["Indirect callback target controlled; live target and startup population open.",
                          "Function-pointer relocation validated in isolated ELF, final image layout open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
