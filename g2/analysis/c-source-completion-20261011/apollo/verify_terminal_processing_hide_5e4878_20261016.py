#!/usr/bin/env python3
"""Compare Terminal processing-label wrapper to pinned stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_processing_hide_5e4878.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-processing-hide-5e4878"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_lv_object_call_450500(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_lv_object_call_441488(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "processing-hide-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "processing-hide-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_processing_hide_5e4878",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, object_value):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        calls = {
            ((symbols["audio_lv_object_call_450500"] if compiled else 0x450500)&~1): 2,
            ((symbols["audio_lv_object_call_441488"] if compiled else 0x441488)&~1): 3}
        trace = []

        def hook(cpu, pc, size, _):
            count = calls.get(pc)
            if count is None:
                return
            registers = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)
            trace.append((pc == next(iter(calls)), *tuple(cpu.reg_read(reg)
                          for reg in registers[:count])))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, object_value)
        entry = symbols["audio_terminal_processing_hide_5e4878"] if compiled else 0x5e4878
        u.emu_start(entry|1, 0x600000, count=1000)
        return trace

    values = (0, 1, 0x100000, 0x20001000, 0xffffffff)
    for object_value in values:
        stock = run(False, object_value)
        selected = run(True, object_value)
        if stock != selected:
            raise RuntimeError(f"processing wrapper mismatch {object_value=:#x}: "
                               f"{stock} vs {selected}")
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_PROCESSING_HIDE_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": len(values),
              "scope": "null and non-null object values, exact two-call sequence and arguments",
              "limits": ["The two LVGL child effects and object lifetime remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(values), sha(receipt))


if __name__ == "__main__":
    main()
