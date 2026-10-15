#!/usr/bin/env python3
"""Compare selected native/C FlashDB GC move effects at lower boundaries."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/settings_flashdb_gc_move.c"
BLOB = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
OUT = G2 / "build/c-firmware/20261014/main-flashdb-gc-move"
SHIM = """#include <stdint.h>
uint32_t audio_flashdb_kv_delete(void*a,const char*b,void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_flashdb_space_search(void*a,void*b,uint32_t c)
{(void)a;(void)b;(void)c;return -1;}
void *audio_settings_copy_text(void*a,const void*b,uint32_t n)
{uint8_t*d=a;const uint8_t*s=b;for(uint32_t i=0;i<n;i++)d[i]=s[i];return a;}
uint32_t g2_flashdb_find_no_cache(uint32_t a,const char*b,void*c)
{(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_write_status(uint32_t a,uint32_t b,uint8_t*c,uint32_t d,uint32_t e,uint32_t f)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t g2_flashdb_flash_read(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_flashdb_flash_write(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e)
{(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
void g2_flashdb_cache_update(void*a,const char*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
void *g2_flashdb_sector_cache_lookup(uint32_t a,uint32_t b)
{(void)a;(void)b;return 0;}
void __aeabi_memclr4(void*p,uint32_t n){uint8_t*q=p;while(n--)*q++=0;}
void __aeabi_memclr(void*p,uint32_t n){uint8_t*q=p;while(n--)*q++=0;}
"""

with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    (temp / "shim.c").write_text(SHIM)
    elf = temp / "gc.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_flashdb_gc_move",
                    str(SOURCE), str(temp / "shim.c"), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        parsed = ELFFile(stream)
        segments = [(item["p_vaddr"], item.data()) for item in parsed.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    names = {"delete": ("audio_flashdb_kv_delete", 0x5448b4),
             "search": ("audio_flashdb_space_search", 0x544814),
             "find": ("g2_flashdb_find_no_cache", 0x54447a),
             "status": ("g2_flashdb_write_status", 0x5858d8),
             "read": ("g2_flashdb_flash_read", 0x585a12),
             "write": ("g2_flashdb_flash_write", 0x585a52),
             "cache": ("g2_flashdb_cache_update", 0x543d1c),
             "lookup": ("g2_flashdb_sector_cache_lookup", 0x543cc0)}

    def run(compiled, mode, kind, length, sector_state=0):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, BLOB)
        cpu.mem_map(0x100000, 0x100000)
        cpu.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        db, kv = 0x20081000, 0x20082000
        cpu.mem_write(db + 0xc, struct.pack("<I", 0x1000))
        cpu.mem_write(db + 0x31, b"\x01")
        cpu.mem_write(kv, bytes((kind, 0, 5)))
        cpu.mem_write(kv + 8, struct.pack("<I", length))
        cpu.mem_write(kv + 0xc, struct.pack("<I", 0x120))
        cpu.mem_write(kv + 0x10, b"alpha\0")
        cpu.mem_write(kv + 0x50, struct.pack("<I", 0x5000))
        effects = []
        addresses = {(symbols[name] & ~1) if compiled else native: label
                     for label, (name, native) in names.items()}

        def hook(engine, address, size, _):
            label = addresses.get(address)
            if label is None:
                return
            r0, r1, r2, r3 = [engine.reg_read(reg) for reg in
                              (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]
            if label == "search":
                effects.append((label, r0, r2))
                engine.mem_write(r1 + 1, bytes((sector_state,)))
                engine.mem_write(r1 + 4, struct.pack("<I", 0x4000))
                engine.mem_write(r1 + 0x10, struct.pack("<I", 0x50))
                result = 0xffffffff if mode == "no_space" else 0x6000
            elif label == "delete":
                effects.append((label, r0, r3))
                result = 0
            elif label == "find":
                effects.append((label, r0))
                result = 1 if mode == "duplicate" else 0
            elif label == "status":
                sp = engine.reg_read(UC_ARM_REG_SP)
                index, sync = struct.unpack("<II", engine.mem_read(sp, 8))
                effects.append((label, r0, r1, r3, index, sync))
                result = 0
            elif label == "read":
                effects.append((label, r0, r1, r3))
                engine.mem_write(r2, bytes([0x42])*r3)
                result = 0
            elif label == "write":
                effects.append((label, r0, r1, r3, bytes(engine.mem_read(r2, r3))))
                result = 0
            elif label == "cache":
                effects.append((label, r0, r2, r3))
                result = 0
            else:
                effects.append((label, r0, r1))
                result = 0x20083000
            engine.reg_write(UC_ARM_REG_R0, result)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.reg_write(UC_ARM_REG_R0, db)
        cpu.reg_write(UC_ARM_REG_R1, kv)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        entry = (symbols["audio_flashdb_gc_move"] & ~1) if compiled else 0x5449c0
        cpu.emu_start(entry | 1, 0x600000, count=30000)
        return (cpu.reg_read(UC_ARM_REG_R0) & 0xff, effects,
                bytes(cpu.mem_read(0x20083000, 24)))

    cases = 0
    for mode, kind, length, sector_state in (("no_space", 2, 12, 0), ("no_space", 3, 12, 0),
                                             ("duplicate", 3, 12, 0), ("copy", 2, 12, 0),
                                             ("copy", 3, 40, 0), ("copy", 3, 80, 0),
                                             ("copy", 3, 40, 1), ("copy", 3, 40, 2)):
        native = run(False, mode, kind, length, sector_state)
        candidate = run(True, mode, kind, length, sector_state)
        assert native == candidate, (mode, kind, length, sector_state, native, candidate)
        cases += 1
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FLASHDB_GC_MOVE_ORACLE",
               "cases": cases, "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "native_entry": "0x5449c0",
               "limits": ["Lower flash, cache and space-search operations are intercepted; physical flash and full-image behavior remain unproved."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)
