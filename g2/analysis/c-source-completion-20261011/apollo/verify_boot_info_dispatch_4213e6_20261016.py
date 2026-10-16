#!/usr/bin/env python3
"""Stock/C INFO read dispatcher comparison with the resident ROM read bounded."""
from pathlib import Path
import hashlib
import itertools
import json
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
ELF = ROOT / "g2/build/c-source-completion-20261011/apollo/bootloader_m33_query_oracle.elf"
SOURCE = ROOT / "g2/components/bootloader/application_storage/device_wait_service.c"
OUTPUT = ROOT / "g2/build/c-firmware/20261016/boot-info-dispatch-4213e6/receipt.json"
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
with ELF.open("rb") as handle:
    image = ELFFile(handle)
    segments = [(part["p_vaddr"], part.data()) for part in image.iter_segments() if part["p_type"] == "PT_LOAD"]
    symbols = {item.name: item["st_value"] for item in image.get_section_by_name(".symtab").iter_symbols()
               if item.name and item["st_shndx"] != "SHN_UNDEF"}


def invoke(source, fixture, visited):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for address, size in ((0x410000, 0x35000), (0x08000000, 0x100000), (0x20000000, 0x40000),
                          (0x40000000, 0x300000)):
        cpu.mem_map(address, size)
    cpu.mem_write(0x410000, blob)
    if source:
        for address, data in segments:
            cpu.mem_write(address, data)
    cpu.mem_write(0x400201bc, struct.pack("<I", fixture["source_state"]))
    cpu.mem_write(0x40021008, struct.pack("<I", fixture["ready_state"]))
    cpu.mem_write(0x20001000, b"\xa5" * 64)
    done = False
    events = []
    rom_read = (symbols["opencfw_boot_info_rom_read"] & ~1) if source else 0x41d28a
    def code(uc, pc, size, _):
        nonlocal done
        if pc == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and 0x4213e6 <= pc < 0x421548:
            visited.update(range(pc, pc + size))
        if pc == rom_read:
            address = cpu.reg_read(a.UC_ARM_REG_R0)
            destination = cpu.reg_read(a.UC_ARM_REG_R1)
            count = cpu.reg_read(a.UC_ARM_REG_R2)
            events.append(["rom-read", address, "buffer" if destination == 0x20001000 else destination, count])
            if destination and count <= 16:
                for word in range(count):
                    cpu.mem_write(destination + 4 * word, struct.pack("<I", 0x87654321 + word))
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, fixture["space"])
    cpu.reg_write(a.UC_ARM_REG_R1, fixture["offset"])
    cpu.reg_write(a.UC_ARM_REG_R2, fixture["count"])
    cpu.reg_write(a.UC_ARM_REG_R3, 0x20001000 if fixture["destination"] else 0)
    entry = (symbols["opencfw_boot_info_read_dispatch"] & ~1) if source else 0x4213e6
    try:
        cpu.emu_start(entry | 1, 0, count=100000)
    except UcError as error:
        raise RuntimeError((source, fixture, hex(cpu.reg_read(a.UC_ARM_REG_PC)))) from error
    assert done, (source, fixture, "instruction limit")
    return {"return": cpu.reg_read(a.UC_ARM_REG_R0),
            "output": bytes(cpu.mem_read(0x20001000, 64)).hex(), "events": events}


fixtures = [{"space": space, "offset": offset, "count": count,
             "source_state": source_state, "ready_state": ready_state,
             "destination": destination}
            for space, offset, count, source_state, ready_state, destination in itertools.product(
                (0, 1, 2, 3, 4, 5, 6, 0x101, 0xffffffff),
                (0, 0x3f, 0x40, 0x1ff, 0x200, 0x2bf, 0x2c0, 0x5ff, 0x600, 0xffffffff),
                (0, 1, 2, 8, 12), (0, 8, 16, 24), (0, 1 << 27), (False, True))]
visited = set()
results = []
for fixture in fixtures:
    stock = invoke(False, fixture, visited)
    selected = invoke(True, fixture, visited)
    if stock != selected:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.with_suffix(".failure.json").write_text(json.dumps({"fixture": fixture, "stock": stock,
            "selected": selected}, indent=2) + "\n")
        raise AssertionError(fixture)
    results.append({"fixture": fixture, "result": stock})
report = {"status": "PASS_NATIVE_BOOT_INFO_DISPATCH_4213E6", "cases": len(results),
          "stock_body_bytes_354": len(visited),
          "unvisited_stock_bytes": [hex(address) for address in sorted(set(range(0x4213e6, 0x421548)) - visited)],
          "stock_sha256": hashlib.sha256(blob).hexdigest(), "selected_elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results,
          "limits": ["The resident ROM read is controlled in both runs; INFO source/ready state is synthetic MMIO.",
                     "This compares the selected M33 C body against stock instructions, not production M55 or physical OTP/MRAM behavior."]}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["cases"], report["stock_body_bytes_354"])
