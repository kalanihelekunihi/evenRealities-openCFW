#!/usr/bin/env python3
"""Compare two ASR-state Terminal FSM actions against pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_asr_start_5e5a7e.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-start-5e5a7e"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t audio_terminal_ui_timer_state_20073c38[0x18];
const uint8_t *audio_td_state_ptr(void){return 0;}
void audio_terminal_ui_notification_restore_5ebfae(uint32_t a){(void)a;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
"""
ENTRIES = [(0x5e5a7e, "audio_terminal_ui_action_5e5a7e"),
           (0x5e5a94, "audio_terminal_ui_action_5e5a94")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5e8124-0x438000:0x5e8128-0x438000], "little") != 0x20073c38:
        raise RuntimeError("ASR timer stock pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "asr-action-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "asr-action-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_action_5e5a7e",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, entry, flag, tick, old_state):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = 0x20001000
        u.mem_write(state+0x802, struct.pack("<H", flag))
        timer = symbols["audio_terminal_ui_timer_state_20073c38"] if compiled else 0x20073c38
        u.mem_write(timer, b"\xa5"*0x18)
        cuts = {
            ((symbols["audio_td_state_ptr"] if compiled else 0x597318)&~1): "state",
            ((symbols["audio_terminal_ui_notification_restore_5ebfae"] if compiled else 0x5ebfae)&~1): "restore",
            ((symbols["g2_flashdb_candidate_tick"] if compiled else 0x4490cc)&~1): "tick",
            ((symbols["audio_log_flags"] if compiled else 0x43d0ce)&~1): "flags"}
        trace = []
        def hook(cpu, pc, size, _):
            kind = cuts.get(pc)
            if kind is None:
                return
            trace.append((kind, cpu.reg_read(A.UC_ARM_REG_R0)) if kind == "restore" else (kind,))
            if kind == "state":
                cpu.reg_write(A.UC_ARM_REG_R0, state)
            elif kind == "tick":
                cpu.reg_write(A.UC_ARM_REG_R0, tick)
            elif kind == "flags":
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, old_state)
        address, name = entry
        u.emu_start((symbols[name] if compiled else address)|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(timer, 0x18)).hex(), trace

    cases = 0
    for entry in ENTRIES:
        for flag in (0, 1, 0xffff):
            for tick in (0, 100, 0xfffffff0):
                for old_state in (4, 5, 0xff):
                    stock = run(False, entry, flag, tick, old_state)
                    selected = run(True, entry, flag, tick, old_state)
                    if stock != selected:
                        raise RuntimeError(f"ASR action mismatch {entry[1]} {flag=} {tick=} "
                                           f"{old_state=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_ASR_START_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "two FSM actions, ASR timer state and lower-call trace",
              "limits": ["Notification-restore child effect, enabled logging, real tick and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
