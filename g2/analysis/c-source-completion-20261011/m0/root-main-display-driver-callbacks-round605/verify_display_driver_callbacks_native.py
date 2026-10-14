#!/usr/bin/env python3
"""Compare native and C display-driver callback effects and diagnostics."""
from pathlib import Path
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).with_name("display_driver_callbacks.c")
BLOB = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
SHIM = """#include <stdint.h>
void audio_display_driver_thread_entry(void *p){(void)p;}
void *audio_thread_new(void (*a)(void *),void *b,const void *c){(void)a;(void)b;(void)c;return 0;}
void *audio_queue_new(uint32_t a,uint32_t b,const void *c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
"""
with tempfile.TemporaryDirectory() as directory:
    shim = Path(directory) / "shim.c"
    shim.write_text(SHIM)
    obj = Path(directory) / "callbacks.o"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-c", str(SOURCE), "-o", str(obj)], check=True)
    with obj.open("rb") as stream:
        object_elf = ELFFile(stream)
        relocations = object_elf.get_section_by_name(".rel.data")
        assert relocations is not None
        symtab = object_elf.get_section(relocations["sh_link"])
        pointers = {(reloc["r_offset"], symtab.get_symbol(reloc["r_info_sym"]).name)
                    for reloc in relocations.iter_relocations()}
        assert pointers == {(0, "audio_display_driver_thread_init"),
                            (4, "audio_display_driver_queue_init")}, pointers
    image = Path(directory) / "callbacks.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_display_driver_thread_init", str(SOURCE),
                    str(SOURCE.with_name("display_driver_attributes.c")), str(shim),
                    "-o", str(image)], check=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        manager_symbol = next(symbol for symbol in elf.get_section_by_name(".symtab").iter_symbols()
                              if symbol.name == "audio_display_driver_manager")
        assert manager_symbol["st_size"] == 16
    cases = [("thread", 0x473952, "audio_display_driver_thread_init", 0x4490e2,
              "audio_thread_new", "audio_display_driver_thread_attrs", 0x75381c, 8),
             ("queue", 0x4739fc, "audio_display_driver_queue_init", 0x449a32,
              "audio_queue_new", "audio_display_driver_queue_attrs", 0x2000067c, 12)]
    for label, native_entry, source_entry, native_api, source_api, attr, native_attr, slot in cases:
        for result in (0, 0x2000abcd):
          for flags_mask in (0, 1, 2, 4, 5, 6, 7):
            observations = []
            for compiled in (False, True):
                cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                cpu.mem_map(0x400000, 0x400000)
                cpu.mem_write(0x438000, BLOB)
                cpu.mem_map(0x100000, 0x200000)
                cpu.mem_map(0x20000000, 0x100000)
                for address, data in segments:
                    cpu.mem_write(address, data)
                manager = symbols["audio_display_driver_manager"] if compiled else 0x20000658
                cpu.mem_write(manager+8, b"\0" * 8)
                api = (symbols[source_api] if compiled else native_api) & ~1
                flags = (symbols["audio_log_flags"] if compiled else 0x43d0ce) & ~1
                extended = (symbols["audio_log_extended"] if compiled else 0x43d574) & ~1
                compact = (symbols["compressed_log_output"] if compiled else 0x43ce9e) & ~1
                calls = []
                def c_string(uc, address):
                    value = bytearray()
                    for offset in range(200):
                        byte = uc.mem_read(address + offset, 1)[0]
                        if byte == 0: break
                        value.append(byte)
                    return bytes(value).decode("ascii", "replace")
                def cut(uc, address, _size, _user):
                    if address == api:
                        a = uc.reg_read(UC_ARM_REG_R0)
                        b = uc.reg_read(UC_ARM_REG_R1)
                        c = uc.reg_read(UC_ARM_REG_R2)
                        if label == "thread":
                            assert a == (symbols["audio_display_driver_thread_entry"] if compiled else 0x473c45)
                            assert b == 0
                        else:
                            assert (a, b) == (0x60, 0x24)
                        assert c == (symbols[attr] if compiled else native_attr)
                        calls.append((label, result))
                        uc.reg_write(UC_ARM_REG_R0, result)
                        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                    elif address == flags:
                        uc.reg_write(UC_ARM_REG_R0, flags_mask)
                        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                    elif address == extended:
                        sp = uc.reg_read(UC_ARM_REG_SP)
                        line = int.from_bytes(uc.mem_read(sp, 4), "little")
                        message = int.from_bytes(uc.mem_read(sp+4, 4), "little")
                        extra = int.from_bytes(uc.mem_read(sp+8, 4), "little") if result else None
                        calls.append(("extended", uc.reg_read(UC_ARM_REG_R0),
                                      c_string(uc, uc.reg_read(UC_ARM_REG_R1)),
                                      c_string(uc, uc.reg_read(UC_ARM_REG_R2)),
                                      c_string(uc, uc.reg_read(UC_ARM_REG_R3)),
                                      line, c_string(uc, message), extra))
                        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                    elif address == compact:
                        calls.append(("compact", uc.reg_read(UC_ARM_REG_R0),
                                      c_string(uc, uc.reg_read(UC_ARM_REG_R1)),
                                      c_string(uc, uc.reg_read(UC_ARM_REG_R2)),
                                      uc.reg_read(UC_ARM_REG_R3) if result else None))
                        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                cpu.hook_add(UC_HOOK_CODE, cut)
                cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
                cpu.reg_write(UC_ARM_REG_LR, 0x600001)
                cpu.emu_start((symbols[source_entry] if compiled else native_entry) | 1,
                              0x600000, count=500)
                observations.append((calls, bytes(cpu.mem_read(manager+8, 8))))
            assert observations[0] == observations[1], (label, result, flags_mask, observations)
print("PASS_DISPLAY_DRIVER_CALLBACKS_NATIVE", len(cases) * 2 * 7)
