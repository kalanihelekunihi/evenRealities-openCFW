#!/usr/bin/env python3
"""Compare simple EvenAI ready actions against stock with controlled callees."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP,
                               UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_ready_4e20f2.c"
OUT = G2 / "build/c-firmware/20261016/main-even-ai-ready-simple-oracle"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
uint8_t audio_even_ai_service_state_2006ed10[0x218];
uint8_t audio_even_ai_ready_state_2006f138[0x218];
uint8_t audio_even_ai_config_state_20074974[3];
uint8_t audio_uart_display_state[2];
uint32_t audio_even_ai_text_stream_handle_20074c04;
uint8_t audio_even_ai_text_pending_200f39b4[0x400];
uint8_t audio_even_ai_text_merged_200f3db4[0x400];
void audio_even_ai_state_lock_4e1fa6(void){}
void audio_even_ai_state_unlock_4e1fbe(void){}
uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t x){(void)x;return 1;}
uint8_t audio_ux_get_system_ble_status(void){return 1;}
uint32_t audio_even_ai_app_acquire_54f380(uint32_t x){(void)x;return 0;}
void audio_even_ai_timer_start_all_4e31a0(uint32_t x){(void)x;}
void audio_even_ai_init_text_stream_4e551e(void){}
void audio_even_ai_stop_current_streaming_4e557c(uint32_t x){(void)x;}
void audio_even_ai_common_timer_stop_4e2e86(void){}
void audio_even_ai_display_ctrl_4e1fd2(uint32_t x,const void*p,uint32_t n){(void)x;(void)p;(void)n;}
const char *audio_text_stream_pending_text_552ce8(uint32_t x){(void)x;return "";}
uint32_t audio_text_stream_set_text_552c20(uint32_t a,const char*b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_text_stream_copy_bytes_553274(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint8_t audio_even_ai_stream_interval_get_4e550a(void){return 25;}
void audio_even_ai_ancc_state_sync_497cf0(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_even_ai_sync_remote_4973f4(uint32_t a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, action, kind, prior, no_reply,
        present=1, refresh=1, ble=1, skill_param=0xa5a5a5a5,
        text_length=3, log_mode=0, allowed=1):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for address, data in segments:
        cpu.mem_write(address, data)
    names = ("audio_even_ai_service_state_2006ed10", "audio_even_ai_ready_state_2006f138",
             "audio_even_ai_config_state_20074974", "audio_uart_display_state",
             "audio_even_ai_text_pending_200f39b4")
    native = (0x2006ed10, 0x2006f138, 0x20074974, 0x20074f2c, 0x200f39b4)
    addresses = dict(zip(names, (sy[x] for x in names) if compiled else native))
    event = bytearray([0xa5] * 0x218)
    event[1], event[2] = action, kind
    event[0x13:0x16] = b"\x01\x21\x43"
    event[0x16:0x18] = text_length.to_bytes(2, "little")
    event[0x18:0x18 + text_length] = (b"abc" if text_length == 3
                                     else b"A" * text_length)
    event[0x0c:0x10] = skill_param.to_bytes(4, "little")
    state = bytearray([0xa5] * 0x218)
    state[0], state[1], state[0x0d] = prior, 1, allowed
    cpu.mem_write(addresses[names[0]], bytes(event))
    cpu.mem_write(addresses[names[1]], bytes(state))
    cpu.mem_write(addresses[names[2]], b"\x01\x92\x34")
    cpu.mem_write(addresses[names[3]], bytes([present, 0]))
    cpu.mem_write(addresses[names[4]], bytes([0xa5]) * 0x400)
    handle_address = (sy["audio_even_ai_text_stream_handle_20074c04"]
                      if compiled else 0x20074c04)
    cpu.mem_write(handle_address, (0x20003000).to_bytes(4, "little"))
    cpu.mem_write(0x20003100, b"pre\x00")
    merged_address = (sy["audio_even_ai_text_merged_200f3db4"]
                      if compiled else 0x200f3db4)
    cpu.mem_write(merged_address, bytes([0xa5]) * 0x400)
    cpu.reg_write(UC_ARM_REG_R0, no_reply)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    calls = []
    logs = []
    native_hooks = {
        0x43d0ce: "log", 0x4e1fa6: "lock", 0x4e1fbe: "unlock",
        0x43d574: "extended", 0x43ce9e: "compressed",
        0x4e1fd2: "display", 0x4e31a0: "timer", 0x4e551e: "init",
        0x4e557c: "stop", 0x4e2e86: "timer_stop", 0x54f380: "acquire",
        0x47d8ce: "ble", 0x4434d0: "refresh", 0x443484: "display_available",
        0x4e550a: "interval", 0x552c20: "set_text", 0x553274: "copy_text",
        0x552ce8: "pending_text",
        0x497cf0: "ancc_sync", 0x4973f4: "remote_sync"}
    compiled_hooks = {
        "audio_even_ai_state_lock_4e1fa6": "lock",
        "audio_even_ai_state_unlock_4e1fbe": "unlock",
        "audio_even_ai_display_ctrl_4e1fd2": "display",
        "audio_even_ai_timer_start_all_4e31a0": "timer",
        "audio_even_ai_init_text_stream_4e551e": "init",
        "audio_even_ai_stop_current_streaming_4e557c": "stop",
        "audio_even_ai_common_timer_stop_4e2e86": "timer_stop",
        "audio_even_ai_app_acquire_54f380": "acquire",
        "audio_ux_get_system_ble_status": "ble",
        "audio_quicklist_refresh_enabled_4434d0": "refresh",
        "audio_even_ai_stream_interval_get_4e550a": "interval",
        "audio_text_stream_set_text_552c20": "set_text",
        "audio_text_stream_copy_bytes_553274": "copy_text",
        "audio_text_stream_pending_text_552ce8": "pending_text",
        "audio_even_ai_ancc_state_sync_497cf0": "ancc_sync",
        "audio_even_ai_sync_remote_4973f4": "remote_sync"}
    compiled_hooks.update({"audio_log_flags": "log",
                           "audio_log_extended": "extended",
                           "compressed_log_output": "compressed"})
    hooks = {sy[key] & ~1: value for key, value in compiled_hooks.items()} if compiled else native_hooks
    def cstring(machine, pointer):
        return bytes(machine.mem_read(pointer, 240)).split(b"\0", 1)[0].decode("ascii")
    def intercept(machine, pc, size, unused):
        name = hooks.get(pc)
        if name is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        if name == "display":
            ptr = machine.reg_read(UC_ARM_REG_R1)
            n = machine.reg_read(UC_ARM_REG_R2)
            calls.append((name, r0 & 255, bytes(machine.mem_read(ptr, n)) if ptr else b""))
        elif name == "set_text":
            ptr = machine.reg_read(UC_ARM_REG_R1)
            raw = bytes(machine.mem_read(ptr, 128)).split(b"\0", 1)[0]
            calls.append((name, r0, raw, machine.reg_read(UC_ARM_REG_R2),
                          machine.reg_read(UC_ARM_REG_R3),
                          int.from_bytes(machine.mem_read(machine.reg_read(UC_ARM_REG_SP), 4), "little")))
        elif name == "copy_text":
            calls.append((name, r0, machine.reg_read(UC_ARM_REG_R1),
                          machine.reg_read(UC_ARM_REG_R2)))
        elif name == "ancc_sync":
            calls.append((name, r0, machine.reg_read(UC_ARM_REG_R1)))
        elif name == "remote_sync":
            calls.append((name, r0))
        elif name == "extended":
            sp = machine.reg_read(UC_ARM_REG_SP)
            line = int.from_bytes(machine.mem_read(sp, 4), "little")
            fmt = cstring(machine, int.from_bytes(machine.mem_read(sp + 4, 4), "little"))
            first = int.from_bytes(machine.mem_read(sp + 8, 4), "little") if "%d" in fmt else None
            logs.append((name, r0, cstring(machine, machine.reg_read(UC_ARM_REG_R1)),
                         cstring(machine, machine.reg_read(UC_ARM_REG_R2)),
                         cstring(machine, machine.reg_read(UC_ARM_REG_R3)), line, fmt, first))
        elif name == "compressed":
            fmt = cstring(machine, machine.reg_read(UC_ARM_REG_R1))
            first = machine.reg_read(UC_ARM_REG_R3) if "%d" in fmt else None
            logs.append((name, r0, fmt, first))
        elif name in ("timer", "stop", "acquire", "refresh"):
            calls.append((name, r0))
        elif name not in ("log", "display_available", "interval", "pending_text",
                          "extended", "compressed"):
            calls.append((name,))
        if name == "log":
            machine.reg_write(UC_ARM_REG_R0, log_mode)
        elif name == "interval":
            machine.reg_write(UC_ARM_REG_R0, 25)
        elif name == "pending_text":
            machine.reg_write(UC_ARM_REG_R0, 0x20003100)
        elif name in ("display_available", "refresh", "ble"):
            machine.reg_write(UC_ARM_REG_R0, {"display_available": present,
                                              "refresh": refresh, "ble": ble}[name])
        else:
            machine.reg_write(UC_ARM_REG_R0, 0)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_even_ai_ready_4e20f2"] if compiled else 0x4e20f2
    cpu.emu_start(entry | 1, 0x600000, count=20000)
    return (bytes(cpu.mem_read(addresses[names[0]], 0x218)),
            bytes(cpu.mem_read(addresses[names[1]], 0x218)),
            bytes(cpu.mem_read(addresses[names[4]], 0x400)),
            bytes(cpu.mem_read(merged_address, 0x400)), calls, logs)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "ready-simple-stubs.c"
    stub.write_text(STUB)
    elf_path = OUT / "ready-simple-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_even_ai_ready_4e20f2",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = [(1, 1, 5, 1, 1, 1), (1, 1, 3, 1, 1, 1),
             (1, 1, 5, 0, 1, 1), (1, 1, 5, 0, 1, 0),
             (1, 1, 5, 1, 0, 1), (1, 3, 5, 1, 1, 1),
             (1, 2, 5, 1, 1, 1), (3, 0, 5, 1, 1, 1),
             (3, 0, 1, 1, 1, 1), (3, 0, 4, 1, 1, 1),
             (4, 0, 5, 1, 1, 1), (5, 0, 5, 1, 1, 1),
             (6, 1, 5, 1, 1, 1), (6, 3, 5, 1, 1, 1),
             (7, 2, 5, 1, 1, 1), (0, 0, 5, 1, 1, 1)]
    for action, kind, prior, present, refresh, ble in cases:
        for no_reply in (0, 1):
            native = run(payload, segments, sy, False, action, kind, prior, no_reply,
                         present, refresh, ble)
            actual = run(payload, segments, sy, True, action, kind, prior, no_reply,
                         present, refresh, ble)
            if native != actual:
                raise RuntimeError(f"EvenAI ready mismatch {(action, kind, prior, no_reply, present, refresh, ble)}: {native!r} != {actual!r}")
    skill_cases = [(3, 1), (3, 2), (3, 0), (5, 0), (8, 0)]
    for kind, parameter in skill_cases:
        for no_reply in (0, 1):
            native = run(payload, segments, sy, False, 6, kind, 5, no_reply,
                         skill_param=parameter)
            actual = run(payload, segments, sy, True, 6, kind, 5, no_reply,
                         skill_param=parameter)
            if native != actual:
                raise RuntimeError(f"EvenAI skill mismatch {(kind, parameter, no_reply)}: {native!r} != {actual!r}")
    boundary_cases = [(3, 0, 5), (5, 0, 5), (6, 1, 5)]
    for action, kind, prior in boundary_cases:
        for text_length in (0, 1, 0x1ff, 0x200):
            for no_reply in (0, 1):
                native = run(payload, segments, sy, False, action, kind, prior,
                             no_reply, text_length=text_length)
                actual = run(payload, segments, sy, True, action, kind, prior,
                             no_reply, text_length=text_length)
                if native != actual:
                    for segment, (expected, observed) in enumerate(zip(native[:4], actual[:4])):
                        if expected != observed:
                            index = next(i for i, pair in enumerate(zip(expected, observed))
                                         if pair[0] != pair[1])
                            raise RuntimeError(f"EvenAI text mismatch {(action, text_length, no_reply)} segment {segment} offset {index:#x}: {expected[index]:#x} != {observed[index]:#x}")
                    raise RuntimeError(f"EvenAI text call mismatch {(action, text_length, no_reply)}: {native[4]!r} != {actual[4]!r}")
    logging_cases = [(1, 1, 5, 1), (3, 0, 5, 1), (5, 0, 5, 1),
                     (5, 0, 5, 0), (6, 3, 5, 1), (6, 3, 5, 0)]
    for action, kind, prior, allowed in logging_cases:
        for log_mode in (1, 2, 4):
            native = run(payload, segments, sy, False, action, kind, prior, 0,
                         log_mode=log_mode, allowed=allowed)
            actual = run(payload, segments, sy, True, action, kind, prior, 0,
                         log_mode=log_mode, allowed=allowed)
            if native != actual:
                raise RuntimeError(f"EvenAI logging mismatch {(action, kind, allowed, log_mode)}: calls {native[4]!r} != {actual[4]!r}; logs {native[5]!r} != {actual[5]!r}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_EVEN_AI_READY_SIMPLE_C_ORACLE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
        "oracle_elf_sha256": sha(elf_path), "cases": (len(cases) + len(skill_cases) +
                                                        len(boundary_cases) * 4) * 2 +
                                                        len(logging_cases) * 3,
        "scope": "Simple action paths with logger disabled and controlled callees; event/state/pending bytes and call order",
        "limits": ["Text lengths above 0x200 and malformed input remain untested; logger side effects and later variadic values are controlled.",
                   "The ready function is a candidate only and is not linked into Apollo Main."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], receipt["cases"], sha(path))

if __name__ == "__main__":
    main()
