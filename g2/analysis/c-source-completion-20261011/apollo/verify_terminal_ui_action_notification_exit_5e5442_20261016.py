#!/usr/bin/env python3
"""Compare Terminal notification-exit FSM actions and completion callback."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_notification_exit_5e5442.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-notification-exit-5e5442"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_terminal_display_queue_handle;
uint32_t audio_terminal_ui_object_valid_43e2ea(void*a){(void)a;return 0;}
void audio_terminal_fade_out_58c426(uint32_t a,uint32_t b,void(*c)(void))
{(void)a;(void)b;(void)c;}
uint8_t audio_uart_device_role_get(void){return 0;}
void audio_terminal_ui_event_5e5484(uint32_t a,uint32_t b,uint32_t c)
{(void)a;(void)b;(void)c;}
void audio_system_alert_close_464c36(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
void audio_terminal_ui_stop_service_a_5eceb2(void){}
"""
ENTRIES = [(0x5e5420, "audio_terminal_ui_finish_5e5420"),
           (0x5e5442, "audio_terminal_ui_action_5e5442"),
           (0x5ed748, "audio_terminal_ui_action_5ed748")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e5ed0-0x438000:0x5e5ed4-0x438000], "little") != 0x20074a90 or \
            int.from_bytes(blob[0x5e5ff4-0x438000:0x5e5ff8-0x438000], "little") != 0x5e5421:
        raise RuntimeError("Terminal exit stock pointers changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "exit-action-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "exit-action-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e5442",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, root, valid, role, old_state):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        cell = symbols["audio_terminal_display_queue_handle"] if compiled else 0x20074a90
        u.mem_write(cell, root.to_bytes(4, "little"))
        cuts = {
            ((symbols["audio_terminal_ui_object_valid_43e2ea"] if compiled else 0x43e2ea)&~1): "valid",
            ((symbols["audio_terminal_fade_out_58c426"] if compiled else 0x58c426)&~1): "fade",
            ((symbols["audio_uart_device_role_get"] if compiled else 0x45a568)&~1): "role",
            ((symbols["audio_terminal_ui_event_5e5484"] if compiled else 0x5e5484)&~1): "event",
            ((symbols["audio_system_alert_close_464c36"] if compiled else 0x464c36)&~1): "close",
            ((symbols["audio_terminal_ui_stop_service_a_5eceb2"] if compiled else 0x5eceb2)&~1): "cleanup"}
        trace = []
        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            regs = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if kind == "valid":
                trace.append((kind, regs[0]))
                cpu.reg_write(A.UC_ARM_REG_R0, valid)
            elif kind == "fade":
                callback = ((symbols["audio_terminal_ui_finish_5e5420"] | 1)
                            if compiled else 0x5e5421)
                trace.append((kind, regs[0], regs[1], regs[2] == callback))
            elif kind == "role":
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "event":
                trace.append((kind, *regs[:3]))
            elif kind == "close":
                trace.append((kind, *regs))
            elif kind == "cleanup":
                trace.append((kind,))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state)
        address, name = entry
        u.emu_start((symbols[name] if compiled else address)|1, 0x600000, count=10000)
        returned = None if address == 0x5e5420 else u.reg_read(A.UC_ARM_REG_R0)
        return returned, trace, int.from_bytes(u.mem_read(cell, 4), "little")

    cases = 0
    for entry in ENTRIES:
        for root in (0, 0x20041000):
            for valid in (0, 1):
                for role in (0, 1, 2):
                    for old_state in (0, 2, 11):
                        stock = run(False, entry, root, valid, role, old_state)
                        selected = run(True, entry, root, valid, role, old_state)
                        if stock != selected:
                            raise RuntimeError(f"exit action mismatch {entry[1]} {root=} {valid=} "
                                               f"{role=} {old_state=}: {stock} vs {selected}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_NOTIFICATION_EXIT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "exit actions, fade callback pointer, validity and role branches",
              "limits": ["LVGL validity, fade animation and system-alert lower effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
