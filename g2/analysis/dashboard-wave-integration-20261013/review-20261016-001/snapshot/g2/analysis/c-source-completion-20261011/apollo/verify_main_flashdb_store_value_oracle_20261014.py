#!/usr/bin/env python3
"""Compare selected native/C FlashDB KV store effects at lower boundaries."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/settings_flashdb_store_value.c"
BLOB = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
OUT = G2 / "build/c-firmware/20261014/main-flashdb-store-value"
SHIM = """#include <stdint.h>
uint32_t g2_log_candidate_module_length(const uint8_t*p){uint32_t n=0;while(p[n])n++;return n;}
int32_t g2_flashdb_print(const char*f,...){(void)f;return 0;}
uint32_t g2_flashdb_db_path(uint32_t a){(void)a;return 0;}
int32_t audio_flashdb_prepare_space(void*a,void*b,uint32_t c)
{(void)a;(void)b;(void)c;return -1;}
uint32_t g2_flashdb_write_status(uint32_t a,uint32_t b,uint8_t*c,uint32_t d,uint32_t e,uint32_t f)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t g2_flashdb_flash_write(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e)
{(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t g2_flashdb_crc32(uint32_t a,const void*b,uint32_t c)
{(void)a;(void)b;(void)c;return 0;}
void g2_flashdb_cache_update(void*a,const char*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
void *g2_flashdb_sector_cache_lookup(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
"""

with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    (temp / "shim.c").write_text(SHIM)
    elf = temp / "store.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_flashdb_store_value",
                    str(SOURCE), str(temp / "shim.c"), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        parsed = ELFFile(stream)
        segments = [(item["p_vaddr"], item.data()) for item in parsed.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    names = {"length": ("g2_log_candidate_module_length", 0x44a43c),
             "print": ("g2_flashdb_print", 0x4733ee),
             "path": ("g2_flashdb_db_path", 0x585c94),
             "prepare": ("audio_flashdb_prepare_space", 0x544af2),
             "status": ("g2_flashdb_write_status", 0x5858d8),
             "write": ("g2_flashdb_flash_write", 0x585a52),
             "crc": ("g2_flashdb_crc32", 0x585840),
             "cache": ("g2_flashdb_cache_update", 0x543d1c),
             "lookup": ("g2_flashdb_sector_cache_lookup", 0x543cc0)}

    def run(compiled, key_length, sector_size, existing_address, prepare_result, fail_at=0,
            sector_state=0):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, BLOB)
        cpu.mem_map(0x100000, 0x100000)
        cpu.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        db, sector, key, value = 0x20081000, 0x20082000, 0x20083000, 0x20084000
        cpu.mem_write(db, struct.pack("<I", 0x20085000))
        cpu.mem_write(db + 0xc, struct.pack("<I", sector_size))
        cpu.mem_write(0x20085000, b"demo\0")
        cpu.mem_write(sector + 1, bytes((sector_state,)))
        cpu.mem_write(sector + 4, struct.pack("<I", 0x6000))
        cpu.mem_write(sector + 0x10, struct.pack("<I", 0x50))
        cpu.mem_write(sector + 0x14, struct.pack("<I", existing_address))
        cpu.mem_write(key, b"a"*key_length + b"\0")
        cpu.mem_write(value, b"data")
        effects = []
        mutating_calls = [0]
        addresses = {(symbols[name] & ~1) if compiled else native: label
                     for label, (name, native) in names.items()}

        def string(engine, pointer):
            return bytes(engine.mem_read(pointer, 200)).split(b"\0")[0]

        def hook(engine, address, size, _):
            label = addresses.get(address)
            if label is None:
                return
            r0, r1, r2, r3 = [engine.reg_read(reg) for reg in
                              (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)]
            if label == "length":
                effects.append((label, string(engine, r0)))
                result = key_length
            elif label == "print":
                effects.append((label, string(engine, r0)))
                result = 0
            elif label == "path":
                effects.append((label, r0))
                result = 0x20085000
            elif label == "prepare":
                effects.append((label, r0, r2))
                result = prepare_result
            elif label == "crc":
                data = bytes(engine.mem_read(r1, r2))
                effects.append((label, r0, data))
                result = (r0 + sum(data) + r2) & 0xffffffff
            elif label == "status":
                sp = engine.reg_read(UC_ARM_REG_SP)
                index, sync = struct.unpack("<II", engine.mem_read(sp, 8))
                effects.append((label, r0, r1, r3, index, sync,
                                bytes(engine.mem_read(r2, 24)) if r3 == 6 else None))
                mutating_calls[0] += 1
                result = 3 if mutating_calls[0] == fail_at else 0
            elif label == "write":
                effects.append((label, r0, r1, r3, bytes(engine.mem_read(r2, r3))))
                mutating_calls[0] += 1
                result = 3 if mutating_calls[0] == fail_at else 0
            elif label == "cache":
                effects.append((label, r0, r2, r3, string(engine, r1)))
                result = 0
            else:
                effects.append((label, r0, r1))
                result = 0
            engine.reg_write(UC_ARM_REG_R0, result)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.reg_write(UC_ARM_REG_R0, db)
        cpu.reg_write(UC_ARM_REG_R1, sector)
        cpu.reg_write(UC_ARM_REG_R2, key)
        cpu.reg_write(UC_ARM_REG_R3, value)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.mem_write(0x200ff000, struct.pack("<I", 4))
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        entry = (symbols["audio_flashdb_store_value"] & ~1) if compiled else 0x544d60
        cpu.emu_start(entry | 1, 0x600000, count=50000)
        return cpu.reg_read(UC_ARM_REG_R0) & 0xff, effects, cpu.mem_read(db + 0x30, 2)

    cases = 0
    scenarios = [(65, 0x1000, 0x6000, -1, 0, 0), (5, 0x20, 0x6000, -1, 0, 0),
                 (5, 0x1000, 0xffffffff, -1, 0, 0), (5, 0x1000, 0x6000, -1, 0, 0),
                 (5, 0x1000, 0xffffffff, 0x6000, 0, 0)]
    scenarios += [(5, 0x1000, 0x6000, -1, stage, 0) for stage in range(1, 6)]
    scenarios += [(5, 0x1000, 0x6000, -1, 0, state) for state in (1, 2)]
    for key_length, sector_size, address, prepared, fail_at, sector_state in scenarios:
        native = run(False, key_length, sector_size, address, prepared, fail_at, sector_state)
        candidate = run(True, key_length, sector_size, address, prepared, fail_at, sector_state)
        assert native == candidate, (key_length, sector_size, address, prepared, fail_at, sector_state, native, candidate)
        cases += 1
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FLASHDB_STORE_VALUE_ORACLE",
               "cases": cases, "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "native_entry": "0x544d60",
               "limits": ["Lower FlashDB effects are intercepted; low-level write failures, real flash persistence and hardware remain unproved."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)
