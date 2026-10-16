#!/usr/bin/env python3
"""Compare Terminal mode-set wrapper with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_mode_set_5eae1e.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-mode-set-5eae1e"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_terminal_event_emit_5eadd4(uint32_t a,uint32_t b,const void*c)
{(void)a;(void)b;(void)c;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "mode-set-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "mode-set-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_mode_set_5eae1e",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, mode, mask):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        lower = (symbols["audio_terminal_event_emit_5eadd4"] if compiled else 0x5eadd4)&~1
        trace = []

        def hook(cpu, pc, size, _):
            if pc != lower:
                return
            trace.append((cpu.reg_read(A.UC_ARM_REG_R0),
                          cpu.reg_read(A.UC_ARM_REG_R1),
                          cpu.reg_read(A.UC_ARM_REG_R2)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, mode)
        u.reg_write(A.UC_ARM_REG_R1, mask)
        entry = symbols["audio_terminal_mode_set_5eae1e"] if compiled else 0x5eae1e
        u.emu_start(entry|1, 0x600000, count=1000)
        return trace

    cases = 0
    for mode in (0, 4, 0xff, 0x100, 0xffffffff):
        for mask in (0, 1, 0xffff, 0x10000, 0xffffffff):
            stock = run(False, mode, mask)
            selected = run(True, mode, mask)
            if stock != selected:
                raise RuntimeError(f"mode-set mismatch {mode=:#x} {mask=:#x}: "
                                   f"{stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_MODE_SET_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "byte mode, halfword mask and null payload forwarded to child",
              "limits": ["Event-emitter child effect remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
