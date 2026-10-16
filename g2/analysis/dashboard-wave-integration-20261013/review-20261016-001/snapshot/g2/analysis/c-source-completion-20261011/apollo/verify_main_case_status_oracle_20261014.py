#!/usr/bin/env python3
"""Compare the bounded case-status C body with the authenticated Thumb path."""
import hashlib
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
OBJECT = G2 / "build/c-firmware/20261014/main-case-status/case_status_source.o"
OUT = G2 / "build/c-firmware/20261014/main-case-status/oracle.json"
RAM = {"disabled": 0x20075012, "sensor_a": 0x2007418f, "sensor_b": 0x2007418e}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def segments(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        data = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"]
                   for symbol in elf.get_section_by_name(".symtab").iter_symbols()}
    return data, symbols


def evaluate(image, entry, cells):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_map(0x20000000, 0x100000)
    for address, data in image:
        if data:
            cpu.mem_write(address, data)
    for name, value in cells.items():
        cpu.mem_write(RAM[name], bytes((value,)))
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x300001)
    cpu.emu_start(entry | 1, 0x300000, count=100)
    return cpu.reg_read(UC_ARM_REG_R0)


def main():
    with tempfile.TemporaryDirectory() as directory:
        linked = Path(directory) / "case-status.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                        "--section-start=.g2_ram_20075012=0x20075012",
                        "--section-start=.g2_ram_2007418f=0x2007418f",
                        "--section-start=.g2_ram_2007418e=0x2007418e",
                        "-e", "audio_uart_case_status", "-o", str(linked), str(OBJECT)],
                       check=True)
        native, _ = segments(NATIVE)
        compiled, symbols = segments(linked)
        if symbols["audio_uart_case_status"] < 0x100000:
            raise RuntimeError("compiled case status entry changed")
        cases = []
        for disabled, sensor_a, sensor_b in itertools.product((0, 1, 2), repeat=3):
            cells = {"disabled": disabled, "sensor_a": sensor_a, "sensor_b": sensor_b}
            original = evaluate(native, 0x4acad0, cells)
            candidate = evaluate(compiled, symbols["audio_uart_case_status"], cells)
            if original != candidate:
                raise RuntimeError(f"case status mismatch: {cells}, {original}, {candidate}")
            cases.append({**cells, "return": original})
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_CASE_STATUS_NATIVE_ORACLE",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
               "cases": cases, "case_count": len(cases),
               "limits": ["Bounded function state comparison only; startup and full image remain open."]}
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT))


if __name__ == "__main__":
    main()
