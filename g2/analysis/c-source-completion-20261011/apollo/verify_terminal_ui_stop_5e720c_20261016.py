#!/usr/bin/env python3
"""Compare terminal teardown order, clear extent and queue reset with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_5e720c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-5e720c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = [("voice", 0x5896b4, "audio_terminal_ui_stop_voice_5896b4"),
         ("timer", 0x5e7ec4, "audio_terminal_ui_stop_timer_5e7ec4"),
         ("a", 0x5eceb2, "audio_terminal_ui_stop_service_a_5eceb2"),
         ("b", 0x5ec268, "audio_terminal_ui_stop_service_b_5ec268"),
         ("c", 0x5ebbc6, "audio_terminal_ui_stop_service_c_5ebbc6"),
         ("d", 0x5ec770, "audio_terminal_ui_stop_service_d_5ec770"),
         ("e", 0x5ec9c0, "audio_terminal_ui_stop_service_e_5ec9c0"),
         ("zero", 0x43c0e4, "audio_uart_buffer_zero")]
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_state_base[0x2a0];
uint32_t audio_terminal_display_queue_handle;
void audio_terminal_ui_stop_voice_5896b4(void){}
void audio_terminal_ui_stop_timer_5e7ec4(void){}
void audio_terminal_ui_stop_service_a_5eceb2(void){}
void audio_terminal_ui_stop_service_b_5ec268(void){}
void audio_terminal_ui_stop_service_c_5ebbc6(void){}
void audio_terminal_ui_stop_service_d_5ec770(void){}
void audio_terminal_ui_stop_service_e_5ec9c0(void){}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e7268-0x438000:0x5e726c-0x438000], "little") != 0x2006e0d0 or \
            int.from_bytes(blob[0x5e7b70-0x438000:0x5e7b74-0x438000], "little") != 0x20074a90:
        raise RuntimeError("terminal teardown stock addresses changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "terminal-stop-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "terminal-stop-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_stop_5e720c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, pattern, queue):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        cell = symbols["audio_terminal_display_queue_handle"] if compiled else 0x20074a90
        u.mem_write(state, bytes((pattern,))*0x2a0)
        u.mem_write(cell, queue.to_bytes(4, "little"))
        hooks = {((symbols[s] if compiled else address)&~1): name
                 for name, address, s in CALLS}
        seen = []
        def hook(cpu, pc, size, _):
            name = hooks.get(pc)
            if not name:
                return
            if name == "zero":
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                seen.append((name, r0 == state, r1, r2))
                cpu.mem_write(r0, b"\0"*r1)
            else:
                seen.append((name,))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_stop_5e720c"] if compiled else 0x5e720c
        u.emu_start(entry|1, 0x600000, count=10000)
        return (seen, bytes(u.mem_read(state, 0x2a0)), bytes(u.mem_read(cell, 4)))

    cases = 0
    for pattern in (0, 0x5a, 0xff):
        for queue in (0, 1, 0x12345678):
            stock, selected = run(False, pattern, queue), run(True, pattern, queue)
            if stock != selected:
                raise RuntimeError(f"terminal stop mismatch {pattern} {queue}: {stock[0]} vs {selected[0]}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "seven teardown calls, 0x2a0-byte clear, queue reset",
              "limits": ["Seven lower-call effects and 0x2a0-byte RAM ownership/placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
