#!/usr/bin/env python3
"""Bounded stock/C MSPI mode-enter comparison with explicit lower-call cuts."""
from pathlib import Path
import hashlib
import itertools
import json
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT = Path(__file__).resolve().parents[4]
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "g2/components/bootloader/platform_control/power_domains.c"
BASE_ELF = ROOT / "g2/build/c-source-completion-20261011/apollo/bootloader_m33_query_oracle.elf"
OVERLAY = ROOT / "g2/build/c-firmware/20261016/boot-mspi-m33-overlay/mspi.elf"
OUTPUT = ROOT / "g2/build/c-firmware/20261016/boot-mspi-enter-41bf84/receipt.json"
blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
def elf_info(path):
    with path.open("rb") as handle:
        image = ELFFile(handle)
        segments = [(part["p_vaddr"], part.data()) for part in image.iter_segments() if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in image.get_section_by_name(".symtab").iter_symbols()
                   if item.name and item["st_shndx"] != "SHN_UNDEF"}
    return segments, symbols
base_segments, base_symbols = elf_info(BASE_ELF)
overlay_segments, overlay_symbols = elf_info(OVERLAY)


def invoke(source, fixture, visited):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for address, size in ((0x410000, 0x35000), (0x08000000, 0x100000), (0x20000000, 0x40000),
                          (0x40000000, 0x300000)):
        cpu.mem_map(address, size)
    cpu.mem_write(0x410000, blob)
    if source:
        for address, data in [*base_segments, *overlay_segments]:
            cpu.mem_write(address, data)
    def put(address, value):
        cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))
    def get(address):
        return struct.unpack("<I", cpu.mem_read(address, 4))[0]
    put(0x40021108, fixture["mask"] if fixture["active"] else 0)
    put(0x4002110c, fixture["mask"] if fixture["settled"] else 0)
    put(0x40021008, fixture["gate"])
    put(0x20026e3c, 0x080e0101 if fixture["callback"] else 0)
    cpu.mem_write(0x200271a5, bytes([fixture.get("modebyte", 0)]))
    cpu.mem_write(0x200271a6, bytes([fixture.get("specialbyte", 0)]))
    events, writes = [], []
    done = False
    lower = {
        "descriptor": ((base_symbols["opencfw_boot_control_query_descriptor_copy"] & ~1) if source else 0x41b8f8),
        "clock": ((base_symbols["clock_request"] & ~1) if source else 0x4222f0),
        "special": ((base_symbols["opencfw_boot_power_special_mode"] & ~1) if source else 0x41bae8),
        "poll": ((base_symbols["opencfw_hal_status_poll"] & ~1) if source else 0x41d246),
        "status": ((base_symbols["opencfw_boot_control_delay_status_change"] & ~1) if source else 0x41d21c),
        "delay": ((base_symbols["opencfw_hal_delay_us"] & ~1) if source else 0x41d1c0),
    }
    def code(uc, pc, size, _):
        nonlocal done
        if pc == 0x08000000:
            done = True
            cpu.emu_stop()
            return
        if not source and 0x41bf84 <= pc < 0x41c0be:
            visited.update(range(pc, pc + size))
        if pc == 0x080e0100:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(3)]
            events.append(["callback", regs[0], regs[1], "value" if regs[2] else "null"])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
            cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
            return
        if pc == lower["descriptor"]:
            pointer = cpu.reg_read(a.UC_ARM_REG_R0)
            selector = cpu.reg_read(a.UC_ARM_REG_R1) & 0xff
            for offset, value in enumerate((0x40021108, fixture["mask"], 0x4002110c, fixture["mask"])):
                put(pointer + 4 * offset, value)
            events.append(["descriptor", selector])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
        elif pc == lower["clock"]:
            events.append(["clock", cpu.reg_read(a.UC_ARM_REG_R0), cpu.reg_read(a.UC_ARM_REG_R1)])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
        elif pc == lower["special"]:
            events.append(["special", cpu.reg_read(a.UC_ARM_REG_R0)])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
        elif pc == lower["poll"]:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
            fifth = get(cpu.reg_read(a.UC_ARM_REG_SP))
            events.append(["poll", *regs, fifth])
            if fixture["mirror"]:
                put(regs[1], (get(regs[1]) & ~regs[2]) | (regs[3] & regs[2]))
            cpu.reg_write(a.UC_ARM_REG_R0, fixture["poll_status"])
        elif pc == lower["status"]:
            regs = [cpu.reg_read(getattr(a, f"UC_ARM_REG_R{i}")) for i in range(4)]
            events.append(["status", *regs])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
        elif pc == lower["delay"]:
            events.append(["delay", cpu.reg_read(a.UC_ARM_REG_R0)])
            cpu.reg_write(a.UC_ARM_REG_R0, 0)
        else:
            return
        cpu.reg_write(a.UC_ARM_REG_PC, cpu.reg_read(a.UC_ARM_REG_LR))
    def write(uc, access, address, size, value, _):
        writes.append([address, size, value & ((1 << (size * 8)) - 1)])
    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write, begin=0x40000000, end=0x402fffff)
    cpu.reg_write(a.UC_ARM_REG_SP, 0x2003f000)
    cpu.reg_write(a.UC_ARM_REG_LR, 0x08000001)
    cpu.reg_write(a.UC_ARM_REG_R0, fixture["selector"])
    entry = (overlay_symbols["opencfw_bl_mspi_mode_enter"] & ~1) if source else 0x41bf84
    try:
        cpu.emu_start(entry | 1, 0, count=100000)
    except UcError as error:
        raise RuntimeError((source, fixture, hex(cpu.reg_read(a.UC_ARM_REG_PC)))) from error
    assert done, (source, fixture)
    return {"return": cpu.reg_read(a.UC_ARM_REG_R0), "irq": cpu.reg_read(a.UC_ARM_REG_PRIMASK),
            "events": events, "writes": writes,
            "registers": [get(address) for address in (0x40021108, 0x4002110c)]}


fixtures = [{"selector": selector, "mask": mask, "active": active, "settled": settled,
             "gate": gate, "callback": callback, "mirror": mirror, "poll_status": poll_status}
            for selector, mask, active, settled, gate, callback, mirror, poll_status in itertools.product(
                (19, 20, 21, 22, 23, 24, 28, 29, 30, 31, 32, 33, 34, 255),
                (1, 4, 0xc0, 0x400), (False, True), (False, True), (0, 1 << 27),
                (False, True), (False, True), (0, 6))]
fixtures.extend({"selector": 20, "mask": 1, "active": False, "settled": False,
                 "gate": 0, "callback": True, "mirror": True, "poll_status": 0,
                 "modebyte": modebyte, "specialbyte": specialbyte}
                for modebyte, specialbyte in itertools.product((0, 1, 3), (0, 3)))
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
report = {"status": "PASS_NATIVE_BOOT_MSPI_ENTER_41BF84", "cases": len(results),
          "stock_body_bytes_314": len(visited),
          "unvisited_stock_bytes": [hex(address) for address in sorted(set(range(0x41bf84, 0x41c0be)) - visited)],
          "stock_sha256": hashlib.sha256(blob).hexdigest(), "base_elf_sha256": hashlib.sha256(BASE_ELF.read_bytes()).hexdigest(),
          "overlay_elf_sha256": hashlib.sha256(OVERLAY.read_bytes()).hexdigest(),
          "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "results": results,
          "limits": ["Descriptor, clock, special power, poll, delay/status and callback targets are controlled in both runs.",
                     "M33 source overlay is a comparison input; production M55, ROM timing and hardware are outside this oracle."]}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
print(report["status"], report["cases"], report["stock_body_bytes_314"])
