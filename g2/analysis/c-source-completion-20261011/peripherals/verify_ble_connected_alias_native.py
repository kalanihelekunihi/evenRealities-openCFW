#!/usr/bin/env python3
"""Compare native and compiled connected checks through their shared mode."""
from pathlib import Path
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[3]
blob = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
src = ROOT / "components/audio/uart_thread_source_candidate"
with tempfile.TemporaryDirectory() as directory:
    elf_path = Path(directory) / "connected.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_ble_is_connected",
                    str(src / "display_ble_connected.c"),
                    str(src / "display_ble_connection_modes.c"), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    assert symbols["audio_ble_connection_marker"] == symbols["audio_ble_current_conn_mode"]
    for value in (0, 0xa3, 0xa4, 0xff):
        results = []
        for compiled in (False, True):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            cpu.mem_map(0x20000000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cell = symbols["audio_ble_current_conn_mode"] if compiled else 0x20004542
            cpu.mem_write(cell, bytes([value]))
            cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(UC_ARM_REG_LR, 0x600001)
            entry = symbols["audio_ble_is_connected"] if compiled else 0x4780f8
            cpu.emu_start(entry | 1, 0x600000, count=50)
            results.append(cpu.reg_read(UC_ARM_REG_R0))
        assert results == [int(value == 0xa3)] * 2, (value, results)
print("PASS_BLE_CONNECTED_ALIAS_NATIVE", 4)
