#!/usr/bin/env python3
"""Compare Nema mode command traffic from native and C execution."""
import hashlib
import itertools
import json
import random
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/nema_mode.c"
CACHE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/nema_cache.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RESULT = Path(__file__).with_name("ambiq-nema-mode-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

with tempfile.TemporaryDirectory(prefix="g2-nema-mode-") as folder:
    folder = Path(folder)
    stub = folder / "stub.c"
    stub.write_text("#include <stdint.h>\n"
                    "void __aeabi_memclr4(void *p,uint32_t n){uint8_t *b=p;"
                    "for(uint32_t i=0;i<n;i++)b[i]=0;}\n"
                    "volatile uint8_t audio_uart_nema_boot_state_200043a8[8];\n"
                    "volatile uint32_t audio_uart_ambiq_unit_cell[1];\n"
                    "volatile uint32_t nema_sink;\n"
                    "__attribute__((noinline)) uint32_t audio_uart_nema_child_514846(uint32_t a,uint32_t b)"
                    "{nema_sink=a^b;return 0;}\n"
                    "void display_driver_nema_select_522a16(uint32_t a)"
                    "{audio_uart_nema_child_514846(0x12c,a);}\n"
                    "void audio_uart_nema_instruction_upload_522920(const uint32_t *p,"
                    "uint32_t n,uint32_t v){audio_uart_nema_child_514846(0xc4,v);"
                    "for(uint32_t i=0;i<n;i++){audio_uart_nema_child_514846(0xc8,p[2*i]);"
                    "audio_uart_nema_child_514846(0xcc,p[2*i+1]);}}\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(CACHE), str(stub),
                    "-o", str(image)], cwd=ROOT, check=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, args, state_flags, unit_flag, state_word):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        state = 0x200043a8 if native else symbols["audio_uart_nema_boot_state_200043a8"]
        cell = 0x20074efc if native else symbols["audio_uart_ambiq_unit_cell"]
        cpu.mem_write(state, bytes(state_flags) + b"\0\0" + state_word.to_bytes(4, "little"))
        cpu.mem_write(cell, (0x20080000).to_bytes(4, "little"))
        cpu.mem_write(0x20080000, b"\0" * 10 + bytes([unit_flag]) + b"\0" * 21)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        for reg, val in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                             UC_ARM_REG_R3), args):
            cpu.reg_write(reg, val)
        child = 0x514846 if native else symbols["audio_uart_nema_child_514846"] & ~1
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address == child:
                events.append((uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
                uc.reg_write(UC_ARM_REG_R0, 0)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x513924 if native else symbols["display_driver_nema_mode_513924"]
        cpu.emu_start(entry | 1, 0, count=2000)
        assert done[0], (native, args, events)
        return events, bytes(cpu.mem_read(0x20080000, 32))

    cases = []
    for mode, target, blend, source, state_flags, unit_flag in itertools.product(
        (1, 0x101, 0, 0x1000001, 0x80000001, 0x20403, 0x11000000),
        (0, 1), (0xffffffff, 0, 2), (0xffffffff, 0, 2),
        ((0, 0), (1, 0), (1, 1)), (0, 1)):
        cases.append(((mode, target, blend, source), state_flags, unit_flag, 0x1234))
    for fmt, bits, target, source, unit_flag in itertools.product(
        range(16), (0, 0x01000000, 0x02000000, 0x08000000,
                    0x10000000, 0x20000000, 0x40000000, 0x80000000),
        (0, 2), (0, 2), (0, 1)):
        cases.append(((bits | fmt | ((fmt & 3) << 8), target,
                       0xffffffff, source), (0, 0), unit_flag, 0x4567))
    rng = random.Random(0x513924)
    for _ in range(640):
        mode = (rng.getrandbits(12) << 20) | rng.getrandbits(12)
        target = rng.choice((0, 1, 2, 3, 4, 0xffffffff))
        blend = rng.choice((0, 1, 2, 3, 4, 0xffffffff))
        source = rng.choice((0, 1, 2, 3, 4, 0xffffffff))
        flags = rng.choice(((0, 0), (1, 0), (1, 1)))
        unit = rng.choice((0, 1))
        cases.append(((mode, target, blend, source), flags, unit, rng.getrandbits(16)))
    for args, flags, unit, word in cases:
        expected = run(True, args, flags, unit, word)
        actual = run(False, args, flags, unit, word)
        assert expected == actual, (args, flags, unit, expected, actual)

body = PAYLOAD[0x513924-0x438000:0x513e2e-0x438000]
receipt = {"status": "PASS_AMBIQ_NEMA_MODE_NATIVE", "cases": len(cases),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "native_body_start": "0x513924", "native_body_end_inclusive": "0x513e2d",
           "native_body_sha256": hashlib.sha256(body).hexdigest(),
           "limits": ["Child Nema register writes are entry-cut and compared as ordered events",
                      "Synthetic state does not prove physical GPU behavior"]}
RESULT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
