#!/usr/bin/env python3
"""Qualify the two returning paths of boot thread-name getter 0x418372."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP,
                               UC_ARM_REG_LR, UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/bootloader/thread_creation/thread_name_getter.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
RESULT = Path(__file__).with_name("boot-thread-name-native-results.json")
NATIVE = STOCK.read_bytes()
assert hashlib.sha256(NATIVE).hexdigest() == "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"

with tempfile.TemporaryDirectory(prefix="g2-boot-thread-name-") as folder:
    folder = Path(folder)
    stub = folder / "stub.c"
    stub.write_text("#include <stdint.h>\nvolatile uint32_t sink;\n"
                    "__attribute__((noinline)) uint32_t opencfw_bl_mask_interrupts(void)"
                    "{sink=1;return 0;}\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stub),
                    "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, task, current):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x40000)
        cpu.mem_write(0x410000, NATIVE)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x600000, 0x1000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        cpu.mem_write(0x20027134, current.to_bytes(4, "little"))
        cpu.reg_write(UC_ARM_REG_R0, task)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            if address == (0x41b2f8 if native else symbols["opencfw_bl_mask_interrupts"] & ~1):
                raise AssertionError(("unexpected fatal path", native, task, current))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x418372 if native else symbols["opencfw_boot_thread_name_get"]
        try:
            cpu.emu_start(entry | 1, 0, count=100)
        except Exception as error:
            raise AssertionError((native, task, current,
                                  hex(cpu.reg_read(UC_ARM_REG_PC)))) from error
        assert done[0], (native, task, current)
        return cpu.reg_read(UC_ARM_REG_R0)

    cases = 0
    for task, current in itertools.product(
        (0, 0x20001000, 0x20004000, 0x20020000, 0x2007fff0),
        (0x20002000, 0x20003000, 0x20060000)):
        assert run(True, task, current) == run(False, task, current)
        cases += 1

    candidate_entry = symbols["opencfw_boot_thread_name_get"] & ~1
    candidate_code = next(data[candidate_entry - address:] for address, data in segments
                          if address <= candidate_entry < address + len(data))
    instructions = list(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(candidate_code[:36],
                                                               candidate_entry))
    stores = [ins.address for ins in instructions
              if ins.mnemonic == "str" and ins.op_str == "r1, [r0]"]
    assert len(stores) == 1
    candidate_store = stores[0]

    def fatal_intent(native):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x40000)
        cpu.mem_write(0x410000, NATIVE)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        cpu.mem_write(0x20027134, (0).to_bytes(4, "little"))
        cpu.reg_write(UC_ARM_REG_R0, 0)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        helper = 0x41b2f8 if native else symbols["opencfw_bl_mask_interrupts"] & ~1
        store = 0x41838c if native else candidate_store
        events = []

        def hook(uc, address, _size, _user):
            if address == helper:
                events.append(("mask",))
                uc.reg_write(UC_ARM_REG_R0, 0)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == store:
                destination = uc.reg_read(UC_ARM_REG_R1 if native else UC_ARM_REG_R0)
                value = uc.reg_read(UC_ARM_REG_R0 if native else UC_ARM_REG_R1)
                events.append(("store_intent", destination, value))
                uc.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x418372 if native else candidate_entry
        cpu.emu_start(entry | 1, 0, count=100)
        return events

    fatal_events = fatal_intent(True)
    assert fatal_events == fatal_intent(False)
    assert fatal_events == [("mask",), ("store_intent", 0xffffffff, 0)]

body = NATIVE[0x418372 - 0x410000:0x418394 - 0x410000]
receipt = {
    "status": "PASS_BOOT_THREAD_NAME_NATIVE_BOUNDED",
    "cases": cases, "fatal_path_events": fatal_events,
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "stock_sha256": hashlib.sha256(NATIVE).hexdigest(),
    "native_body_start": "0x418372", "native_body_end_inclusive": "0x418393",
    "native_body_sha256": hashlib.sha256(body).hexdigest(),
    "limits": ["Null task with nonnull current TCB and explicit task paths compared",
               "Fatal null/current-null path matched through the interrupt mask call and pre-store register intent; the invalid write and loop were not executed",
               "No scheduler, memory protection, or physical hardware behavior tested"],
}
RESULT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
