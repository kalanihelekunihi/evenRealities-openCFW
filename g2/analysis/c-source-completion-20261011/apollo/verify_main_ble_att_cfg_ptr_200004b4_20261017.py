#!/usr/bin/env python3
"""Bind the ATT config-pointer cell to authenticated stock startup bytes."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_att_cfg_ptr_200004b4_20261017.c"
BOOT_SOURCE = G2 / "components/bootloader/initializer_callbacks/pcm22_remaining_native/initialized_data.c"
BOOT_VERIFY = G2 / "components/bootloader/startup/verify.py"
OUT = G2 / "build/c-firmware/20261017/main-ble-att-cfg-ptr-ram"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    object_path = OUT / "cfg-ptr.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(object_path)], check=True)
    with object_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbol = next(s for s in elf.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_ble_att_cfg_ptr_200004b4")
        section = elf.get_section(symbol["st_shndx"])
        compiled = section.data()[symbol["st_value"]:symbol["st_value"] + 4]
    assert compiled == struct.pack("<I", 0x20000414)
    assert "0x20000414u,0x20000444u" in BOOT_SOURCE.read_text()
    spec = importlib.util.spec_from_file_location("startup_verify", BOOT_VERIFY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.v.ENTRIES["expand_adapter"] = 0x415326
    machine = module.Machine()
    machine.cpu.mem_write(0x20000000, b"\xa5" * 1371)
    machine.cpu.reg_write(module.v.a.UC_ARM_REG_R9, 0)
    assert machine.run("expand_adapter", [0x433104])["return"] == 0x433110
    stock = bytes(machine.cpu.mem_read(0x200004b4, 4))
    target = bytes(machine.cpu.mem_read(0x20000414, 8))
    assert stock == compiled
    record = {
        "status": "PASS_MAIN_BLE_ATT_CFG_PTR_RAM_SOURCE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "boot_source": str(BOOT_SOURCE.relative_to(ROOT)),
        "boot_source_sha256": sha(BOOT_SOURCE),
        "object_sha256": sha(object_path),
        "stock_record": "0x433104", "stock_cell": "0x200004b4",
        "stock_pointer": "0x20000414", "stock_target_first_8_bytes": target.hex(),
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "remaining_gate": "Startup scatter and final linker placement of the ATT config pointer and target remain unproven.",
    }
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], sha(receipt))


if __name__ == "__main__":
    main()
