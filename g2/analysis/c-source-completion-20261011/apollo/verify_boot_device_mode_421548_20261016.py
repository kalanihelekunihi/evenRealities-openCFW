#!/usr/bin/env python3
"""Execute the stock and selected-C device-mode selector gate with a bounded dispatcher."""
from pathlib import Path
import hashlib
import json
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF = ROOT / "g2/build/c-source-completion-20261011/apollo/bootloader_m33_query_oracle.elf"
SOURCE = ROOT / "g2/components/bootloader/application_storage/device_mode_wait.c"
OUTPUT = ROOT / "g2/build/c-firmware/20261016/boot-device-mode-421548/receipt.json"
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
with ELF.open("rb") as handle:
    image = ELFFile(handle)
    segments = [(part["p_vaddr"], part.data()) for part in image.iter_segments() if part["p_type"] == "PT_LOAD"]
    symbols = {item.name: item["st_value"] for item in image.get_section_by_name(".symtab").iter_symbols()
               if item.name and item["st_shndx"] != "SHN_UNDEF"}


def invoke(source, mode, status, visited):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for address, size in ((0x410000, 0x35000), (0x08000000, 0x100000), (0x20000000, 0x40000)):
        cpu.mem_map(address, size)
    cpu.mem_write(0x410000, blob)
    if source:
        for address, data in segments:
            cpu.mem_write(address, data)
    cpu.mem_write(0x20001000, struct.pack("<I", 0xa5a5a5a5))
    done = False
    events = []
    dispatch = (symbols["opencfw_boot_info_read_dispatch"] & ~1) if source else 0x4213e6
    def code(uc, pc, size, _):
        nonlocal done
        if pc == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and 0x421548 <= pc < 0x42156e:
            visited.update(range(pc, pc + size))
        if pc == dispatch:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
            events.append(regs)
            cpu.mem_write(regs[3], struct.pack("<I", 0x87654321))
            cpu.reg_write(a.UC_ARM_REG_R0, status)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, mode)
    cpu.reg_write(a.UC_ARM_REG_R1, 0x244)
    cpu.reg_write(a.UC_ARM_REG_R2, 1)
    cpu.reg_write(a.UC_ARM_REG_R3, 0x20001000)
    entry = (symbols["opencfw_boot_device_mode_wait"] & ~1) if source else 0x421548
    try:
        cpu.emu_start(entry | 1, 0, count=10000)
    except UcError as error:
        raise RuntimeError((source, mode, status, hex(cpu.reg_read(a.UC_ARM_REG_PC)))) from error
    assert done, (source, mode, status)
    return {"return": cpu.reg_read(a.UC_ARM_REG_R0),
            "output": struct.unpack("<I", cpu.mem_read(0x20001000, 4))[0],
            "events": events, "stack": cpu.reg_read(a.UC_ARM_REG_SP)}


visited = set()
results = []
for mode in [*range(256), 0x101, 0x103, 0x105, 0xffffffff]:
    for status in (0, 6):
        stock = invoke(False, mode, status, visited)
        selected = invoke(True, mode, status, visited)
        if stock != selected:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.with_suffix(".failure.json").write_text(json.dumps({"mode": mode, "status": status,
                "stock": stock, "selected": selected}, indent=2) + "\n")
            raise AssertionError((mode, status))
        results.append({"mode": mode, "status": status, "result": stock})
report = {"status": "PASS_NATIVE_BOOT_DEVICE_MODE_421548", "cases": len(results),
          "stock_body_bytes_38": len(visited),
          "unvisited_stock_bytes": [hex(address) for address in sorted(set(range(0x421548, 0x42156e)) - visited)],
          "stock_sha256": hashlib.sha256(blob).hexdigest(), "selected_elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results,
          "limits": ["The downstream read dispatcher is controlled in both runs; this covers the selector gate only.",
                     "The M33 ELF is a source comparison input; ROM, scheduler, M55 image and hardware behavior are not established."]}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["cases"], report["stock_body_bytes_38"])
