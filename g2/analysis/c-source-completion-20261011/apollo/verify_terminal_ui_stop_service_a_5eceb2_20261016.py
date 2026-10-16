#!/usr/bin/env python3
"""Compare terminal timer/object cleanup guard and state writes with stock."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_service_a_5eceb2.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-a-5eceb2"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_ui_object_valid_43e2ea(void*p){(void)p;return 0;}
void audio_uart_page_delete_event_filter_44d7b8(void*p){(void)p;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5ed9c4-0x438000:0x5ed9c8-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("terminal timer cleanup stock base changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "stop-a-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "stop-a-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_stop_service_a_5eceb2",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, pointer, valid, fill):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        base = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(base, bytes((fill,))*0x2a0)
        u.mem_write(base+0x240, pointer.to_bytes(4, "little"))
        targets = {"valid": (0x43e2ea, "audio_terminal_ui_object_valid_43e2ea"),
                   "delete": (0x44d7b8, "audio_uart_page_delete_event_filter_44d7b8"),
                   "zero": (0x43c0e4, "audio_uart_buffer_zero")}
        hooks = {((symbols[s] if compiled else address)&~1): name
                 for name, (address, s) in targets.items()}
        calls = []
        def hook(cpu, pc, size, _):
            name = hooks.get(pc)
            if not name:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if name == "valid":
                calls.append((name, r0))
                cpu.reg_write(A.UC_ARM_REG_R0, valid)
            elif name == "delete":
                calls.append((name, r0))
            elif name == "zero":
                calls.append((name, r0 == base+0x248, r1, r2))
                cpu.mem_write(r0, b"\0"*r1)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_stop_service_a_5eceb2"] if compiled else 0x5eceb2
        u.emu_start(entry|1, 0x600000, count=10000)
        return bytes(u.mem_read(base+0x240, 0x3e)).hex(), calls

    cases = 0
    for args in itertools.product((0, 1, 0x20080000), (0, 1, 2), (0, 0x5a, 0xff)):
        stock, selected = run(False, *args), run(True, *args)
        if stock != selected:
            raise RuntimeError(f"terminal timer cleanup mismatch {args}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_A_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "object guard, delete call, two words, 0x2c-byte clear, trailing flag",
              "limits": ["Validity and delete lower effects, terminal state-base RAM ownership and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
