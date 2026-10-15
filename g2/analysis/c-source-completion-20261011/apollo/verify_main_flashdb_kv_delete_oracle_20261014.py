#!/usr/bin/env python3
"""Bounded native/C KV deletion failures before status-read integration."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/settings_flashdb_kv_delete.c"
BLOB = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
OUT = G2 / "build/c-firmware/20261014/main-flashdb-kv-delete"
SHIM = """#include <stdint.h>
void __aeabi_memclr4(void *p,uint32_t n){uint8_t *q=p;while(n--)*q++=0;}
uint32_t g2_flashdb_find_kv(uint32_t a,uint32_t b,void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_flashdb_write_status(uint32_t a,uint32_t b,uint8_t*c,uint32_t d,uint32_t e,uint32_t f)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;return 0;}
uint32_t g2_flashdb_flash_read(uint32_t a,uint32_t b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t g2_flashdb_get_status(const uint8_t*a,uint32_t b){(void)a;(void)b;return 0;}
void g2_flashdb_cache_update(void*a,const char*b,uint32_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
uint32_t g2_log_candidate_module_length(const uint8_t*a){(void)a;return 0;}
void *g2_flashdb_sector_cache_lookup(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
"""

with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    (temp / "shim.c").write_text(SHIM)
    elf = temp / "delete.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_flashdb_kv_delete",
                    str(SOURCE), str(temp / "shim.c"), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        parsed = ELFFile(stream)
        segments = [(item["p_vaddr"], item.data()) for item in parsed.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, supplied, final_status, write_result, read_status=0):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, BLOB)
        cpu.mem_map(0x100000, 0x100000)
        cpu.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        db, key, kv = 0x20081000, 0x20082000, 0x20083000
        cpu.mem_write(db + 0xc, struct.pack("<I", 0x1000))
        cpu.mem_write(db + 0xa4, b"\0")
        cpu.mem_write(key, b"alpha\0")
        cpu.mem_write(kv + 0x50, struct.pack("<I", 0x2400))
        cpu.mem_write(kv + 2, b"\x05")
        cpu.mem_write(kv + 0x10, b"alpha\0")
        calls = []
        find = (symbols["g2_flashdb_find_kv"] & ~1) if compiled else 0x54449a
        write = (symbols["g2_flashdb_write_status"] & ~1) if compiled else 0x5858d8
        read = (symbols["g2_flashdb_flash_read"] & ~1) if compiled else 0x585948
        get = (symbols["g2_flashdb_get_status"] & ~1) if compiled else None
        update = (symbols["g2_flashdb_cache_update"] & ~1) if compiled else 0x543d1c
        lookup = (symbols["g2_flashdb_sector_cache_lookup"] & ~1) if compiled else 0x543cc0
        length = (symbols["g2_log_candidate_module_length"] & ~1) if compiled else 0x44a43c

        def hook(engine, address, size, _):
            if address == find:
                calls.append(("find", engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1)))
                engine.reg_write(UC_ARM_REG_R0, 0)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == write:
                sp = engine.reg_read(UC_ARM_REG_SP)
                calls.append(("write", engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1),
                              engine.reg_read(UC_ARM_REG_R3),
                              struct.unpack("<II", engine.mem_read(sp, 8))))
                engine.reg_write(UC_ARM_REG_R0, write_result)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == read:
                calls.append(("read", engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1)))
                engine.reg_write(UC_ARM_REG_R0, read_status if not compiled else 0)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == get:
                engine.reg_write(UC_ARM_REG_R0, read_status)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == update:
                calls.append(("cache", engine.reg_read(UC_ARM_REG_R0),
                              engine.reg_read(UC_ARM_REG_R2), engine.reg_read(UC_ARM_REG_R3)))
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == lookup:
                calls.append(("lookup", engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1)))
                engine.reg_write(UC_ARM_REG_R0, 0x20084000)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == length:
                engine.reg_write(UC_ARM_REG_R0, 5)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.reg_write(UC_ARM_REG_R0, db)
        cpu.reg_write(UC_ARM_REG_R1, key)
        cpu.reg_write(UC_ARM_REG_R2, kv if supplied else 0)
        cpu.reg_write(UC_ARM_REG_R3, final_status)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        entry = (symbols["audio_flashdb_kv_delete"] & ~1) if compiled else 0x5448b4
        cpu.emu_start(entry | 1, 0x600000, count=1000)
        return cpu.reg_read(UC_ARM_REG_R0) & 0xff, cpu.mem_read(db + 0xa4, 1)[0], cpu.mem_read(0x20084002, 1)[0], calls

    cases = 0
    for supplied, final_status, write_result, read_status in ((False, 0, 2, 0), (True, 0, 2, 0),
                                                               (True, 1, 2, 0), (True, 0, 0, 0),
                                                               (True, 1, 0, 0), (True, 1, 0, 1)):
        native = run(False, supplied, final_status, write_result, read_status)
        candidate = run(True, supplied, final_status, write_result, read_status)
        assert native == candidate, (supplied, final_status, write_result, read_status, native, candidate)
        cases += 1
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FLASHDB_KV_DELETE_ORACLE",
               "cases": cases, "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "native_entry": "0x5448b4",
               "limits": ["Selected find, write, cache, and status-read effects are intercepted; real flash timing, low-level status encoding and whole-image behavior remain unproved."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)
