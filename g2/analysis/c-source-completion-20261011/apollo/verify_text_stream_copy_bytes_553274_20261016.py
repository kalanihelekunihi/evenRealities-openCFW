#!/usr/bin/env python3
"""Controlled stock/compiled oracle for text-stream copy and callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_copy_bytes_553274.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-copy-bytes"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
int32_t audio_file_mutex_acquire(void*m,uint32_t t){(void)m;(void)t;return 0;}
int32_t audio_file_mutex_release(void*m){(void)m;return 0;}
uint32_t audio_text_stream_buffer_create_553338(void*a,void*b,uint32_t*c,uint32_t n){(void)a;(void)b;(void)c;(void)n;return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;return a;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, requested, available, notify, mutex, lock_result,
        ensure_result, callback):
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
    for off, value in ((0, 0x20004000), (4, 0x20005000), (0x10, available),
                       (0x18, 0x20007001 if callback else 0),
                       (0x20, 0x20006000 if mutex else 0), (0x24, 0x20)):
        seed[off:off+4] = value.to_bytes(4, "little")
    cpu.mem_write(obj, bytes(seed))
    cpu.mem_write(0x20004000, bytes([0xaa]) * 32)
    cpu.mem_write(0x20005000, b"abcdefghijklmnopqrstuvwxzy012345")
    cpu.reg_write(UC_ARM_REG_R0, obj)
    cpu.reg_write(UC_ARM_REG_R1, requested)
    cpu.reg_write(UC_ARM_REG_R2, notify)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_file_mutex_acquire": "lock", "audio_file_mutex_release": "unlock",
             "audio_text_stream_buffer_create_553338": "ensure",
             "audio_queue_copy_bytes": "copy"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x4497b6: "lock", 0x44981c: "unlock", 0x553338: "ensure",
              0x439be4: "copy"})
    hooks[0x20007000] = "callback"
    calls = []
    def intercept(machine, pc, width, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        r1 = machine.reg_read(UC_ARM_REG_R1)
        r2 = machine.reg_read(UC_ARM_REG_R2)
        if kind == "lock":
            calls.append((kind, r0, r1))
            returned = lock_result
        elif kind == "ensure":
            calls.append((kind, r0, r1, r2, machine.reg_read(UC_ARM_REG_R3)))
            returned = ensure_result
        elif kind == "copy":
            calls.append((kind, r0, r1, r2))
            machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
            returned = r0
        else:
            calls.append((kind, r0))
            returned = 0
        machine.reg_write(UC_ARM_REG_R0, returned)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    entry = sy["audio_text_stream_copy_bytes_553274"] if compiled else 0x553274
    cpu.emu_start(entry | 1, 0x600000, count=3000)
    return (bytes(cpu.mem_read(obj, 0x30)), bytes(cpu.mem_read(0x20004000, 32)), calls)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "copy-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "copy-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_copy_bytes_553274",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for requested, available in ((3, 10), (8, 5), (0x10008, 0x10005)):
        for notify in (0, 1):
            for mutex in (False, True):
                for lock_result in (0, 1):
                    for ensure_result in (0, 1):
                        for callback in (False, True):
                            args = (requested, available, notify, mutex, lock_result,
                                    ensure_result, callback)
                            stock = run(payload, segments, sy, False, *args)
                            actual = run(payload, segments, sy, True, *args)
                            if stock != actual:
                                raise RuntimeError(f"copy mismatch {args}: {stock!r} != {actual!r}")
                            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_COPY_BYTES_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "16-bit clamp, ensure, copy, callback and object bytes",
               "limits": ["Callback, mutex, capacity and copy implementations are controlled hooks."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
