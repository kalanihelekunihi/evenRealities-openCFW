#!/usr/bin/env python3
"""Compare elapsed-time label effects with pinned Apollo stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_elapsed_text_5e48b8.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-elapsed-text-5e48b8"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
void audio_lv_label_set_text_fmt_49954c(uint32_t a,const char*b,...){(void)a;(void)b;}
void audio_lv_obj_invalidate_43dfa4(uint32_t a,uint32_t b){(void)a;(void)b;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e53b4-0x438000:0x5e53b8-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("Apollo stock payload or Terminal state base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "elapsed-text-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "elapsed-text-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_elapsed_text_5e48b8",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, seconds, label):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state+0x1d8, struct.pack("<I", label))
        fmt = (symbols["audio_lv_label_set_text_fmt_49954c"] if compiled else 0x49954c)&~1
        invalid = (symbols["audio_lv_obj_invalidate_43dfa4"] if compiled else 0x43dfa4)&~1
        trace = []

        def read_cstring(addr):
            out = bytearray()
            for i in range(32):
                b = u.mem_read(addr+i, 1)[0]
                if b == 0:
                    return out.decode("ascii")
                out.append(b)
            raise RuntimeError("unterminated elapsed-time format")

        def hook(cpu, pc, size, _):
            if pc == fmt:
                format_text = read_cstring(cpu.reg_read(A.UC_ARM_REG_R1))
                args = [cpu.reg_read(A.UC_ARM_REG_R2)]
                if format_text == "%lum%02lus":
                    args.append(cpu.reg_read(A.UC_ARM_REG_R3))
                trace.append(("format", cpu.reg_read(A.UC_ARM_REG_R0),
                              format_text, *args))
            elif pc == invalid:
                trace.append(("invalidate", cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, seconds)
        entry = symbols["audio_terminal_elapsed_text_5e48b8"] if compiled else 0x5e48b8
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for seconds in (0, 1, 9, 10, 59, 60, 61, 119, 3599, 3600, 0xffff, 0xffffffff):
        for label in (0, 0x20002000, 0x2000f000):
            stock = run(False, seconds, label)
            selected = run(True, seconds, label)
            if stock != selected:
                raise RuntimeError(f"elapsed text mismatch {seconds=} {label=:#x}: "
                                   f"{stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ELAPSED_TEXT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "null and non-null labels, threshold 60, large values, exact format and invalidate call arguments",
              "limits": ["LVGL runtime effects and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
