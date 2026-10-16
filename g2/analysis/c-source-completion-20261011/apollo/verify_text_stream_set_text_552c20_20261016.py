#!/usr/bin/env python3
"""Compare stock and C text-stream set/append orchestration."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_set_text_552c20.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-set-text"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint32_t audio_text_stream_validate_5533cc(void*a,const char*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void audio_text_stream_pause_552d40(void*a){(void)a;}
uint32_t strlen(const char*a){(void)a;return 0;}
uint32_t audio_text_stream_buffer_create_553338(void*a,void*b,void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_text_stream_restart_552db2(void*a){(void)a;}
char *strcat(char*a,const char*b){(void)b;return a;}
char *strcpy(char*a,const char*b){(void)b;return a;}
void audio_text_stream_dispatch_552df0(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_text_stream_next_interval_5532f8(void*a){(void)a;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, object_present, text_present, interval,
        mode, notify, valid_result, ensure_result):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for a, blob in segments:
        cpu.mem_write(a, blob)
    obj = 0x20003000
    seed = bytearray([0xa5] * 0x30)
    seed[4:8] = (0x20005000).to_bytes(4, "little")
    seed[8:12] = (100).to_bytes(4, "little")
    seed[0x10:0x14] = (3).to_bytes(4, "little")
    cpu.mem_write(obj, bytes(seed))
    cpu.mem_write(0x20005000, b"old\0" + bytes([0xa5]) * 28)
    cpu.mem_write(0x20006000, b"new\0")
    cpu.reg_write(UC_ARM_REG_R0, obj if object_present else 0)
    cpu.reg_write(UC_ARM_REG_R1, 0x20006000 if text_present else 0)
    cpu.reg_write(UC_ARM_REG_R2, interval)
    cpu.reg_write(UC_ARM_REG_R3, mode)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.mem_write(0x200ff000, notify.to_bytes(4, "little"))
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_text_stream_validate_5533cc": "validate",
             "audio_text_stream_pause_552d40": "pause", "strlen": "strlen",
             "audio_text_stream_buffer_create_553338": "ensure",
             "audio_text_stream_restart_552db2": "restart", "strcat": "strcat",
             "strcpy": "strcpy", "audio_text_stream_dispatch_552df0": "dispatch",
             "audio_text_stream_next_interval_5532f8": "next"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x5533cc: "validate", 0x552d40: "pause", 0x44a43c: "strlen",
              0x553338: "ensure", 0x552db2: "restart", 0x567c80: "strcat",
              0x48d540: "strcpy", 0x552df0: "dispatch", 0x5532f8: "next"})
    calls = []
    def cstring(p):
        return bytes(cpu.mem_read(p, 32)).split(b"\0", 1)[0]
    def intercept(machine, pc, width, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        r1 = machine.reg_read(UC_ARM_REG_R1)
        r2 = machine.reg_read(UC_ARM_REG_R2)
        r3 = machine.reg_read(UC_ARM_REG_R3)
        if kind == "validate":
            calls.append((kind, r0, cstring(r1), r2))
            returned = valid_result
        elif kind == "strlen":
            calls.append((kind, cstring(r0)))
            returned = len(cstring(r0))
        elif kind == "ensure":
            calls.append((kind, r0, r1, r2, r3))
            returned = ensure_result
        elif kind in ("strcat", "strcpy"):
            calls.append((kind, r0, cstring(r1)))
            left = cstring(r0) if kind == "strcat" else b""
            machine.mem_write(r0, left + cstring(r1) + b"\0")
            returned = r0
        elif kind == "dispatch":
            calls.append((kind, r0, r1, r2))
            returned = 0
        else:
            calls.append((kind, r0))
            returned = 42 if kind == "next" else 0
        machine.reg_write(UC_ARM_REG_R0, returned)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_text_stream_set_text_552c20"] if compiled else 0x552c20
    cpu.emu_start(entry | 1, 0x600000, count=3000)
    return (cpu.reg_read(UC_ARM_REG_R0), bytes(cpu.mem_read(obj, 0x30)),
            bytes(cpu.mem_read(0x20005000, 32)), calls)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "set-text-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "set-text-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_set_text_552c20",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for obj, text in ((False, True), (True, False), (True, True)):
        for interval in (0, 25):
            for mode in (0, 1, 2, 0x101):
                for notify in (0, 1, 0x100):
                    for valid in (0, 1):
                        for ensure in (0, 1):
                            args = (obj, text, interval, mode, notify, valid, ensure)
                            stock = run(payload, segments, sy, False, *args)
                            actual = run(payload, segments, sy, True, *args)
                            if stock != actual:
                                raise RuntimeError(f"set-text mismatch {args}: {stock!r} != {actual!r}")
                            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_SET_TEXT_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Five-argument ABI, validation, append/replace, ensure, dispatch, return",
               "limits": ["Helper effects and malformed inputs remain controlled or untested."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
