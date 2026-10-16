#!/usr/bin/env python3
"""Bounded stock versus selected-C shared-memory startup body comparison."""
from pathlib import Path
import hashlib
import itertools
import json
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ELF = ROOT / "g2/build/c-source-completion-20261011/apollo/bootloader_m33_query_oracle.elf"
OVERLAY = ROOT / "g2/build/c-firmware/20261016/boot-memory-m33-overlay/memory.elf"
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OUTPUT = ROOT / "g2/build/c-firmware/20261016/boot-shared-memory-41be36/receipt.json"
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
with ELF.open("rb") as handle:
    image = ELFFile(handle)
    segments = [(part["p_vaddr"], part.data()) for part in image.iter_segments() if part["p_type"] == "PT_LOAD"]
    symbols = {item.name: item["st_value"] for item in image.get_section_by_name(".symtab").iter_symbols()
               if item.name and item["st_shndx"] != "SHN_UNDEF"}

with OVERLAY.open("rb") as handle:
    overlay_image = ELFFile(handle)
    overlay_segments = [(part["p_vaddr"], part.data()) for part in overlay_image.iter_segments() if part["p_type"] == "PT_LOAD"]
    overlay_symbols = {item.name: item["st_value"] for item in overlay_image.get_section_by_name(".symtab").iter_symbols()
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
        for address, data in overlay_segments:
            cpu.mem_write(address, data)
    def put(address, value):
        cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))
    def get(address):
        return struct.unpack("<I", cpu.mem_read(address, 4))[0]
    cpu.mem_write(0x20001000, bytes(fixture["config"]))
    for address, value in fixture["seeds"].items():
        put(int(address, 16), value)
    events, writes = [], []
    done = False
    power = (symbols["opencfw_boot_power_callback"] & ~1) if source else 0x41cd1a
    poll = (symbols["opencfw_hal_status_poll"] & ~1) if source else 0x41d246
    def code(uc, pc, size, _):
        nonlocal done
        if pc == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and 0x41be36 <= pc < 0x41bf3a:
            visited.update(range(pc, pc + size))
        if pc == power:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(3)]
            events.append(["power", regs[0], regs[1], "config" if regs[2] else "null"])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == poll:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
            fifth = get(cpu.reg_read(a.UC_ARM_REG_SP))
            events.append(["poll", *regs, fifth])
            if fixture["mirror"]:
                put(0x40021028, (get(0x40021028) & ~7) | (get(0x40021024) & 7))
            cpu.reg_write(a.UC_ARM_REG_R0, fixture["poll_status"])
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    def write(uc, access, address, size, value, _):
        writes.append([address, size, value & ((1 << (size * 8)) - 1)])
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write, begin=0x40000000, end=0x402fffff)
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, 0x20001000)
    cpu.reg_write(a.UC_ARM_REG_R1, 0x13579bdf)
    cpu.reg_write(a.UC_ARM_REG_R2, 0x2468ace0)
    cpu.reg_write(a.UC_ARM_REG_R3, 0xdeadbeef)
    entry = (overlay_symbols["opencfw_boot_startup_shared_memory"] & ~1) if source else 0x41be36
    try:
        cpu.emu_start(entry | 1, 0, count=100000)
    except UcError as error:
        raise RuntimeError((source, fixture, hex(cpu.reg_read(a.UC_ARM_REG_PC)))) from error
    assert done, (source, fixture, "instruction limit")
    return {"return": cpu.reg_read(a.UC_ARM_REG_R0), "events": events, "writes": writes,
            "registers": {hex(address): get(address) for address in (0x40021024, 0x40021028, 0x4002102c, 0x40021040)}}


fixtures = []
for current, desired, last, mode, mirror, poll_status in itertools.product(
        (0, 3, 7), (0, 1, 4, 7), (0, 1, 2, 3, 7, 8), (0, 0xffffffff), (False, True), (0, 6)):
    config = [desired, 3, 5, 6, last]
    fixtures.append({"config": config, "mirror": mirror, "poll_status": poll_status,
                     "seeds": {"0x40021024": mode, "0x40021028": current,
                               "0x4002102c": mode, "0x40021040": mode}})
visited = set()
results = []
for fixture in fixtures:
    stock = invoke(False, fixture, visited)
    selected = invoke(True, fixture, visited)
    if stock != selected:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.with_suffix(".failure.json").write_text(json.dumps({"fixture": fixture, "stock": stock, "selected": selected}, indent=2) + "\n")
        raise AssertionError(fixture)
    results.append({"fixture": fixture, "result": stock})
report = {"status": "PASS_NATIVE_BOOT_SHARED_MEMORY_41BE36", "cases": len(results),
          "stock_body_bytes_260": len(visited),
          "stock_sha256": hashlib.sha256(blob).hexdigest(), "selected_elf_sha256": hashlib.sha256(ELF.read_bytes()).hexdigest(),
          "overlay_elf_sha256": hashlib.sha256(OVERLAY.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256((ROOT / "g2/components/bootloader/initializer_callbacks/startup_memory_config.c").read_bytes()).hexdigest(),
          "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results,
          "limits": ["Power callback and status poll are controlled in both runs; optional poll mirroring models status convergence.",
                     "Cortex-M33 selected comparison ELF is a source oracle, not production M55 image execution or hardware proof."]}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["cases"], report["stock_body_bytes_260"])
