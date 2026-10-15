#!/usr/bin/env python3
"""Compare native and C ring packets for both request paths."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
SOURCE = ROOT / "components/audio/uart_thread_source_candidate/ring_sync.c"
TEMPLATES = ROOT / "components/audio/uart_thread_source_candidate/display_ring_template_data.c"
SHIM = """#include <stdint.h>
const volatile uint8_t *const audio_uart_ring_status_word=(volatile uint8_t *)0x20075043u;
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t audio_uart_request_send(uint32_t x,const void *p,uint32_t n,uint32_t q)
{(void)x;(void)p;(void)n;(void)q;return 0;}
"""

with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    (temp / "shim.c").write_text(SHIM)
    elf = temp / "ring.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_ring_sync_active",
                    str(SOURCE), str(TEMPLATES), str(temp / "shim.c"), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        parsed = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in parsed.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, active, role, status):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        uc.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, BLOB)
        uc.mem_map(0x100000, 0x100000)
        uc.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_write(0x20075043, bytes((status,)))
        getter = (symbols["audio_uart_device_role_get"] & ~1) if compiled else 0x45a568
        sender = (symbols["audio_uart_request_send"] & ~1) if compiled else 0x4651e0
        result = []

        def hook(engine, address, size, _):
            if address == getter:
                engine.reg_write(UC_ARM_REG_R0, role)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
            elif address == sender:
                result.append((engine.reg_read(UC_ARM_REG_R0),
                               bytes(engine.mem_read(engine.reg_read(UC_ARM_REG_R1), 8)),
                               engine.reg_read(UC_ARM_REG_R2), engine.reg_read(UC_ARM_REG_R3)))
                engine.reg_write(UC_ARM_REG_R0, 0)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(UC_ARM_REG_LR, 0x600001)
        name = "audio_uart_ring_sync_active" if active else "audio_uart_ring_sync_idle"
        entry = (symbols[name] & ~1) if compiled else (0x47ced6 if active else 0x47cf28)
        uc.emu_start(entry | 1, 0x600000, count=10000)
        assert len(result) == 1, result
        return result[0]

    count = 0
    for active in (False, True):
        for role in (0, 1, 2, 255):
            for status in (0, 15, 16, 31, 255):
                native = run(False, active, role, status)
                candidate = run(True, active, role, status)
                assert native == candidate, (active, role, status, native, candidate)
                count += 1
    receipt = {
        "status": "PASS_RING_SYNC_NATIVE_C_SOURCE_CORRECTION",
        "cases": count,
        "native_entries": ["0x47ced6", "0x47cf28"],
        "sources": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (SOURCE, TEMPLATES)},
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["The existing Main archive still contains the earlier ring_sync.o and requires a source archive refresh.",
                   "Fixed placement, full image link, and hardware behavior remain open."],
    }
    output = ROOT / "build/c-firmware/20261014/ring-sync-correction"
    output.mkdir(parents=True, exist_ok=True)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS_RING_SYNC_NATIVE", count)
