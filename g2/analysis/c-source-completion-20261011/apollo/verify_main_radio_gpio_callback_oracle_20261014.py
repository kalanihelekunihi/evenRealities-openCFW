#!/usr/bin/env python3
"""Native/C effect comparison for the Apollo radio GPIO callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/radio_gpio_callback_bridge.c"
BLOB = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
OUT = G2 / "build/c-firmware/20261014/main-radio-gpio-callback"
SHIM = """#include <stdint.h>
uint32_t audio_ble_wsf_set_event(uint32_t id,uint32_t mask)
{(void)id;(void)mask;return 0;}
"""

with tempfile.TemporaryDirectory() as temporary:
    temp = Path(temporary)
    (temp / "shim.c").write_text(SHIM)
    elf = temp / "callback.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,opencfw_radio_gpio_callback",
                    str(SOURCE), str(temp / "shim.c"), "-o", str(elf)], check=True)
    with elf.open("rb") as stream:
        parsed = ELFFile(stream)
        segments = [(item["p_vaddr"], item.data()) for item in parsed.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, counter, handler, argument):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, BLOB)
        cpu.mem_map(0x100000, 0x100000)
        cpu.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_write(0x20074640, struct.pack("<I", counter))
        cpu.mem_write(0x20074fcb, bytes((handler,)))
        event = (symbols["audio_ble_wsf_set_event"] & ~1) if compiled else 0x52b91e
        calls = []

        def hook(engine, address, size, _):
            if address == event:
                calls.append((engine.reg_read(UC_ARM_REG_R0),
                              engine.reg_read(UC_ARM_REG_R1),
                              struct.unpack("<I", engine.mem_read(0x20074640, 4))[0]))
                engine.reg_write(UC_ARM_REG_R0, 0)
                engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.reg_write(UC_ARM_REG_R0, argument)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        entry = (symbols["opencfw_radio_gpio_callback"] & ~1) if compiled else 0x4b4a98
        cpu.emu_start(entry | 1, 0x600000, count=100)
        return struct.unpack("<I", cpu.mem_read(0x20074640, 4))[0], calls

    cases = 0
    for counter in (0, 1, 0x7fffffff, 0xffffffff):
        for handler in (0, 1, 7, 255):
            for argument in (0, 0xfeedface):
                native = run(False, counter, handler, argument)
                candidate = run(True, counter, handler, argument)
                assert native == candidate == ((counter + 1) & 0xffffffff,
                                               [(handler, 1, (counter + 1) & 0xffffffff)]), (counter, handler, argument, native, candidate)
                cases += 1
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_RADIO_GPIO_CALLBACK_ORACLE",
               "cases": cases,
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "native_entry": "0x4b4a98", "native_event_provider": "0x52b91e",
               "limits": ["Scheduler event is an effect boundary; asynchronous GPIO/NVIC behavior and hardware remain unproved."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)
