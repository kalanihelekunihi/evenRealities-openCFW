#!/usr/bin/env python3
"""Compare native and compiled hub-role updates against one source cell."""
from pathlib import Path
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[3]
blob = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
src = ROOT / "components/audio/uart_thread_source_candidate"
with tempfile.TemporaryDirectory() as directory:
    getter = Path(directory) / "getter.c"
    getter.write_text("#include <stdint.h>\nuint8_t audio_uart_device_role_get(void){return 0;}\n")
    elf_path = Path(directory) / "hub_role.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_hub_role_init",
                    str(src / "display_hub_role_init.c"),
                    str(src / "display_page_hub_startup_cells.c"), str(getter),
                    "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    for role in (0, 1, 2, 3):
        results = []
        for compiled in (False, True):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            cpu.mem_map(0x20000000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cell = symbols["audio_uart_hub_role_cell"] if compiled else 0x20004526
            cpu.mem_write(cell, b"\x03\x00")
            getter_address = (symbols["audio_uart_device_role_get"] if compiled else 0x45a568) & ~1
            def cut_getter(uc, address, _size, _user):
                if address == getter_address:
                    uc.reg_write(UC_ARM_REG_R0, role)
                    uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, cut_getter)
            cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(UC_ARM_REG_LR, 0x600001)
            entry = symbols["audio_hub_role_init"] if compiled else 0x4a6d28
            cpu.emu_start(entry | 1, 0x600000, count=100)
            results.append(bytes(cpu.mem_read(cell, 2)))
        expected = (2 if role == 2 else 3).to_bytes(2, "little")
        assert results == [expected, expected], (role, results)
print("PASS_HUB_ROLE_INIT_NATIVE", 4)
