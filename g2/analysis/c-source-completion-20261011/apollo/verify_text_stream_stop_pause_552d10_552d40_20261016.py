#!/usr/bin/env python3
"""Compare stock and C text-stream pause/stop behavior in controlled RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_stop_pause_552d10_552d40.c"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-stop-pause"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
int32_t audio_file_mutex_acquire(void*m,uint32_t t){(void)m;(void)t;return 0;}
int32_t audio_file_mutex_release(void*m){(void)m;return 0;}
int32_t audio_timer_stop(void*t){(void)t;return 0;}
"""

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(payload, segments, sy, compiled, entry, present, mutex, timer, lock_result, buffers):
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
    for off, value in ((0, 0x20004000 if buffers else 0),
                       (4, 0x20004100 if buffers else 0),
                       (0x1c, 0x20006000 if timer else 0),
                       (0x20, 0x20005000 if mutex else 0)):
        seed[off:off+4] = value.to_bytes(4, "little")
    cpu.mem_write(obj, bytes(seed))
    cpu.mem_write(0x20004000, b"X")
    cpu.mem_write(0x20004100, b"Y")
    cpu.reg_write(UC_ARM_REG_R0, obj if present else 0)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    names = {"audio_file_mutex_acquire": "lock", "audio_file_mutex_release": "unlock",
             "audio_timer_stop": "timer_stop"}
    hooks = ({sy[k] & ~1: v for k, v in names.items()} if compiled else
             {0x4497b6: "lock", 0x44981c: "unlock", 0x4494d8: "timer_stop"})
    calls = []
    def intercept(machine, pc, width, unused):
        kind = hooks.get(pc)
        if kind is None:
            return
        r0 = machine.reg_read(UC_ARM_REG_R0)
        calls.append((kind, r0, machine.reg_read(UC_ARM_REG_R1)) if kind == "lock" else (kind, r0))
        machine.reg_write(UC_ARM_REG_R0, lock_result if kind == "lock" else 0)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, intercept)
    address = sy[entry] if compiled else (0x552d10 if entry.endswith("552d10") else 0x552d40)
    cpu.emu_start(address | 1, 0x600000, count=2000)
    return (bytes(cpu.mem_read(obj, 0x30)), bytes(cpu.mem_read(0x20004000, 1)),
            bytes(cpu.mem_read(0x20004100, 1)), calls)

def main():
    payload = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PINNED:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "stop-pause-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "stop-pause-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_text_stream_stop_552d10",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        sy = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for entry in ("audio_text_stream_stop_552d10", "audio_text_stream_pause_552d40"):
        for present in (False, True):
            for mutex in (False, True):
                for timer in (False, True):
                    for lock_result in (0, 1):
                        for buffers in (False, True):
                            args = (entry, present, mutex, timer, lock_result, buffers)
                            stock = run(payload, segments, sy, False, *args)
                            actual = run(payload, segments, sy, True, *args)
                            if stock != actual:
                                raise RuntimeError(f"stop/pause mismatch {args}: {stock!r} != {actual!r}")
                            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TEXT_STREAM_STOP_PAUSE_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PINNED, "oracle_elf": str(elf_path.relative_to(ROOT)),
               "oracle_elf_sha256": sha(elf_path), "cases": cases,
               "scope": "Object/buffer bytes, mutex and timer calls for both functions",
               "limits": ["Mutex and timer side effects, full object lifetime remain external."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, sha(path))

if __name__ == "__main__":
    main()
