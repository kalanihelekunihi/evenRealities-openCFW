#!/usr/bin/env python3
"""Compare the terminal timer clear against the pinned stock Apollo payload."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_timer_5e7ec4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-timer-5e7ec4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e8124-0x438000:0x5e8128-0x438000], "little") != 0x20073c38 or \
            blob[0x5e7ec4-0x438000:0x5e7ed4-0x438000].hex() != "10b518210022964c200054f609f910bd":
        raise RuntimeError("terminal timer stock slice changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "timer-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "timer-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_stop_timer_5e7ec4",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, pattern):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_timer_state_20073c38"] if compiled else 0x20073c38
        u.mem_write(state-4, b"\xa5"*0x20)
        u.mem_write(state, bytes((pattern,))*0x18)
        zero = (symbols["audio_uart_buffer_zero"] if compiled else 0x43c0e4)&~1
        calls = []
        def hook(cpu, pc, size, _):
            if pc != zero:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            calls.append((r0 == state, r1, r2))
            cpu.mem_write(r0, b"\0"*r1)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_stop_timer_5e7ec4"] if compiled else 0x5e7ec4
        u.emu_start(entry|1, 0x600000, count=1000)
        return bytes(u.mem_read(state-4, 0x20)).hex(), calls

    cases = 0
    for pattern in (0, 1, 0x5a, 0xff):
        stock, selected = run(False, pattern), run(True, pattern)
        if stock != selected:
            raise RuntimeError(f"timer clear mismatch {pattern}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_TIMER_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "24-byte zero call and four-byte guards on either side",
              "limits": ["Timer RAM startup, consumers, final whole-image placement and hardware behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
