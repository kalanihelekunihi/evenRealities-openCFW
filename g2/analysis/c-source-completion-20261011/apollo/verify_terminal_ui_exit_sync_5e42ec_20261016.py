#!/usr/bin/env python3
"""Compare terminal exit-sync pending and status choice with stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_exit_sync_5e42ec.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-exit-sync-5e42ec"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_mode_sync_pending;
uint32_t audio_settings_terminal_mode(void){return 0;}
uint32_t audio_terminal_send_status_reply(const void*p){(void)p;return 0;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e4764-0x438000:0x5e4768-0x438000], "little") != 0x2006e0d0:
        raise RuntimeError("terminal exit-sync stock contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "exit-sync-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "exit-sync-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_exit_sync_5e42ec",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, pending, mode):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cell = symbols["audio_terminal_mode_sync_pending"] if compiled else 0x2006e344
        u.mem_write(cell, bytes((pending,)))
        mapping = {"zero": (0x43c0e4, "audio_uart_buffer_zero"),
                   "mode": (0x46c630, "audio_settings_terminal_mode"),
                   "send": (0x5ceba2, "audio_terminal_send_status_reply")}
        hooks = {((symbols[s] if compiled else a) & ~1): k
                 for k, (a, s) in mapping.items()}
        calls = []
        def hook(cpu, pc, size, _):
            kind = hooks.get(pc)
            if not kind:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if kind == "zero":
                calls.append((kind, r1, r2))
                cpu.mem_write(r0, b"\0" * r1)
            elif kind == "mode":
                calls.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, mode)
            elif kind == "send":
                calls.append((kind, bytes(cpu.mem_read(r0, 2)).hex()))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_exit_sync_5e42ec"] if compiled else 0x5e42ec
        u.emu_start(entry | 1, 0x600000, count=10000)
        return (bytes(u.mem_read(cell, 1)).hex(), calls)

    cases = 0
    for pending in (0, 1, 2, 255):
        for mode in (0, 1, 2, 255):
            stock, selected = run(False, pending, mode), run(True, pending, mode)
            if stock != selected:
                raise RuntimeError(f"exit-sync mismatch {pending} {mode}: {stock} vs {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_EXIT_SYNC_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "pending byte clear, terminal setting mode and first two status bytes",
              "limits": ["Encoder effect, uninitialized upper stack bytes, final RAM placement and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
