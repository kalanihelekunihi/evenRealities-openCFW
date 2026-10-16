#!/usr/bin/env python3
"""Compare Terminal elapsed-label refresh with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_elapsed_refresh_5e4902.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-elapsed-refresh-5e4902"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_td_counter_b_get(void){return 0;}
uint32_t audio_td_record_elapsed_get_59769c(uint32_t a,uint32_t*b)
{(void)a;(void)b;return 0;}
void audio_terminal_elapsed_text_5e48b8(uint32_t a){(void)a;}
void audio_terminal_elapsed_clear_5e4894(void){}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "elapsed-refresh-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "elapsed-refresh-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_elapsed_refresh_5e4902",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, record, success, seconds):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        names = ("audio_td_counter_b_get",
                 "audio_td_record_elapsed_get_59769c",
                 "audio_terminal_elapsed_text_5e48b8",
                 "audio_terminal_elapsed_clear_5e4894")
        stock = (0x5973dc, 0x59769c, 0x5e48b8, 0x5e4894)
        cuts = {(symbols[name] if compiled else address)&~1: name
                for name, address in zip(names, stock)}
        trace = []

        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            if kind == names[0]:
                trace.append(("counter",))
                cpu.reg_write(A.UC_ARM_REG_R0, record)
            elif kind == names[1]:
                pointer = cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append(("elapsed_get", r0, pointer >= 0x20000000))
                cpu.mem_write(pointer, struct.pack("<I", seconds))
                cpu.reg_write(A.UC_ARM_REG_R0, success)
            elif kind == names[2]:
                trace.append(("format", r0))
            else:
                trace.append(("clear",))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_elapsed_refresh_5e4902"] if compiled else 0x5e4902
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for record in (0, 1, 0x20001000, 0xffffffff):
        for success in (0, 1, 2):
            for seconds in (0, 59, 60, 0xffffffff):
                stock = run(False, record, success, seconds)
                selected = run(True, record, success, seconds)
                if stock != selected:
                    raise RuntimeError(f"elapsed refresh mismatch {record=:#x} "
                                       f"{success=} {seconds=}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ELAPSED_REFRESH_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "counter selection, out-parameter, success and failure branches over 48 cases",
              "limits": ["Counter/elapsed source and clear-child effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
