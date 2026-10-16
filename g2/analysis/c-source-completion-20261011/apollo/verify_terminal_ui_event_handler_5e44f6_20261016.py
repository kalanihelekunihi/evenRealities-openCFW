#!/usr/bin/env python3
"""Compare stock/C terminal UI event routes at controlled lower calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_event_handler_5e44f6.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-event-5e44f6"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = r'''
#include <stdint.h>
uint32_t audio_terminal_display_queue_handle;
uint8_t audio_uart_registry_context_20003e50[8];
uint32_t audio_registry_ring_connect_enter_5e438e(uint32_t x){return x;}
void audio_registry_ring_connect_leave_5e43be(void){}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_tracepoint_reset_pull_478110(uint8_t x){(void)x;}
void audio_ble_status_register_callback(void (*x)(uint32_t,const void*)){(void)x;}
void audio_terminal_runtime_event_callback_1(uint32_t a,const void*b){(void)a;(void)b;}
void audio_terminal_ui_start_5e716c(uint32_t x){(void)x;}
void audio_terminal_ui_status_5e7b74(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_terminal_ui_tick_5e8008(void){}
void audio_terminal_ui_stop_5e720c(void){}
void audio_terminal_ui_exit_sync_5e42ec(void){}
void audio_uart_page_58c238(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
'''
NATIVE = {"zero": 0x43c0e4, "enter": 0x5e438e, "flags": 0x43d0ce,
          "reset": 0x478110, "register": 0x4abcc6, "start": 0x5e716c,
          "status": 0x5e7b74, "fade": 0x58c238, "exit": 0x5e42ec,
          "copy": 0x439be4, "tick": 0x5e8008, "stop": 0x5e720c,
          "leave": 0x5e43be}
SYMBOL = {"zero": "audio_uart_buffer_zero", "enter": "audio_registry_ring_connect_enter_5e438e",
          "flags": "audio_log_flags", "reset": "audio_tracepoint_reset_pull_478110",
          "register": "audio_ble_status_register_callback", "start": "audio_terminal_ui_start_5e716c",
          "status": "audio_terminal_ui_status_5e7b74", "fade": "audio_uart_page_58c238",
          "exit": "audio_terminal_ui_exit_sync_5e42ec", "copy": "audio_uart_checksum_copy",
          "tick": "audio_terminal_ui_tick_5e8008", "stop": "audio_terminal_ui_stop_5e720c",
          "leave": "audio_registry_ring_connect_leave_5e43be"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    if int.from_bytes(blob[0x5e4784-0x438000:0x5e4788-0x438000], "little") != 0x20074a90 or \
            int.from_bytes(blob[0x5e47ac-0x438000:0x5e47b0-0x438000], "little") != 0x20003e50:
        raise RuntimeError("terminal UI stock RAM pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "terminal-ui-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "terminal-ui-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_registry_callback_5e44f6",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, event, length, present, queue, payload):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        context = symbols["audio_uart_registry_context_20003e50"] if compiled else 0x20003e50
        queue_addr = symbols["audio_terminal_display_queue_handle"] if compiled else 0x20074a90
        u.mem_write(context, b"\xa5" * 8)
        u.mem_write(queue_addr, queue.to_bytes(4, "little"))
        pointer = 0x20090000 if present else 0
        u.mem_write(0x20090000, payload)
        hooks = {((symbols[SYMBOL[k]] if compiled else v) & ~1): k for k, v in NATIVE.items()}
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
            elif kind == "copy":
                calls.append((kind, bytes(cpu.mem_read(r1, r2)).hex(), r2))
                cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
            elif kind == "register":
                expected = (symbols["audio_terminal_runtime_event_callback_1"] | 1) if compiled else 0x5e8815
                calls.append((kind, r0 == expected))
            elif kind in ("reset", "start"):
                calls.append((kind, r0))
            elif kind in ("status",):
                calls.append((kind, r0, r1))
            elif kind == "fade":
                calls.append((kind, r0, r1, r2))
            else:
                calls.append((kind,))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_R0, event)
        u.reg_write(A.UC_ARM_REG_R1, pointer)
        u.reg_write(A.UC_ARM_REG_R2, length)
        u.reg_write(A.UC_ARM_REG_R3, 0x12345678)
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_uart_registry_callback_5e44f6"] if compiled else 0x5e44f6
        u.emu_start(entry | 1, 0x600000, count=100000)
        return (u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(context, 8)).hex(), calls)

    cases = 0
    for args in itertools.product((0, 1, 2, 3, 4, 5, 6), (0, 7, 8, 9),
                                  (False, True), (0, 0x1234),
                                  (b"\x02\x01\x03\x04\x78\x56\x34\x12", b"\xff"*8)):
        stock, selected = run(False, *args), run(True, *args)
        if stock != selected:
            raise RuntimeError(f"terminal UI mismatch {args}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_EVENT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "event 0-6, payload guard, queue/context write and lower-call order with logging disabled",
              "limits": ["Enabled logging, real terminal lower-call side effects, context RAM extent and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
