#!/usr/bin/env python3
"""Compare Terminal output-label style wrapper with pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_set_label_style_5e482a.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-set-label-style-5e482a"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_lv_object_call_441488(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
void audio_lv_label_style_call_597ea6(uint32_t a,const void*b,uint32_t c)
{(void)a;(void)b;(void)c;}
void audio_lv_label_style_call_597f10(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_label_style_call_597f52(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_label_style_call_597ee0(uint32_t a){(void)a;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "set-label-style-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "set-label-style-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_set_label_style_5e482a",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, object_value, style, count, scale):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        names = ("audio_lv_object_call_441488", "audio_lv_label_style_call_597ea6",
                 "audio_lv_label_style_call_597f10", "audio_lv_label_style_call_597f52",
                 "audio_lv_label_style_call_597ee0")
        stock = (0x441488, 0x597ea6, 0x597f10, 0x597f52, 0x597ee0)
        cuts = {(symbols[name] if compiled else address)&~1: index
                for index, (name, address) in enumerate(zip(names, stock))}
        trace = []

        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)
            argc = (3, 3, 2, 2, 1)[index]
            trace.append((index, *tuple(cpu.reg_read(reg) for reg in regs[:argc])))
            cpu.reg_write(A.UC_ARM_REG_R0, 0xa5a5a5a5)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                              (object_value, style, count, scale)):
            u.reg_write(reg, value)
        entry = symbols["audio_terminal_set_label_style_5e482a"] if compiled else 0x5e482a
        u.emu_start(entry|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), trace

    cases = 0
    for values in ((0, 0x20001000, 6, 100), (0x20002000, 0, 6, 100),
                   (0x20002000, 0x20001000, 0, 100),
                   (0x20002000, 0x20001000, 6, 0)):
        stock = run(False, *values)
        selected = run(True, *values)
        if stock != selected:
            raise RuntimeError(f"style guard mismatch {values}: {stock} vs {selected}")
        cases += 1
    for count in (1, 6, 0x10000, 0xffffffff):
        for scale in (1, 100, 0xffffffff):
            values = (0x20002000, 0x20001000, count, scale)
            stock = run(False, *values)
            selected = run(True, *values)
            if stock != selected:
                raise RuntimeError(f"style call mismatch {values}: {stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_SET_LABEL_STYLE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "four null guards, multiplication overflow, five lower calls and return value",
              "limits": ["Five lower-call effects and actual style buffer extent remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
