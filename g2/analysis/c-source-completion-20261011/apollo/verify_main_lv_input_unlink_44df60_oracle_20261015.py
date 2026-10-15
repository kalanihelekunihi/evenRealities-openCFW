#!/usr/bin/env python3
"""Compare Apollo input unlink and flag helpers with stock code."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_input_unlink_44df60.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-input-unlink-44df60"
SHIM = '''void audio_uart_lv_input_clear_452f26(void *p,void *q){}'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_input_unlink_44df60",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, present, activity, flags):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            input_obj, obj = 0x20010000, 0x20011000
            u.mem_write(input_obj + 8, bytes([activity]))
            u.mem_write(input_obj + 0xb, bytes([flags]))
            trace = []
            cut = (syms["audio_uart_lv_input_clear_452f26"] & ~1) if compiled else 0x452f26
            def hook(cpu, address, size, user):
                if address != cut: return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((r0, r1, u.mem_read(input_obj + 0xb, 1)[0]))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, input_obj if present else 0)
            u.reg_write(A.UC_ARM_REG_R1, obj)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_input_unlink_44df60"] if compiled else 0x44df60) | 1,
                        0x600000, count=10000)
            return trace, u.mem_read(input_obj + 0xb, 1)[0]
        cases = list(itertools.product((False, True), (0, 1, 3, 0xff), (0, 2, 8, 0x80, 0xff)))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_INPUT_UNLINK_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_spans": ["0x44df60..0x44df7f", "0x452f0c..0x452f17", "0x452fec..0x452ff9"],
               "cases": len(cases),
               "limits": ["Input clear 0x452f26 is controlled; its object/event effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
