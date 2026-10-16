#!/usr/bin/env python3
"""Compare the native lv_obj_set_pos call sequence and null assertion."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_pos_43f09a.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY_SHA = "a9fe79b614907d95aea1cc90e59bb470ca08d8120d08110190a0d49f55c17096"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
assert hashlib.sha256(IMAGE[0x43f09a-0x438000:0x43f0e0-0x438000]).hexdigest() == BODY_SHA
OUT = G2 / "build/c-firmware/20261015/main-obj-set-pos-43f09a"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_43f0e0(uint32_t a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_43f142(uint32_t a,uint32_t b){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43f09a",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, object_, x, y):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        for reg, word in ((A.UC_ARM_REG_R0, object_), (A.UC_ARM_REG_R1, x),
                          (A.UC_ARM_REG_R2, y), (A.UC_ARM_REG_SP, 0x2000f000),
                          (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, word)
        hooks = ({0x44d25c: "log", 0x43f0e0: "x", 0x43f142: "y"} if not compiled
                 else {symbols["audio_uart_lvgl_log"] & ~1: "log",
                       symbols["audio_uart_page_43f0e0"] & ~1: "x",
                       symbols["audio_uart_page_43f142"] & ~1: "y"})
        seen = []

        def string(address):
            return bytes(uc.mem_read(address, 160)).split(b"\0")[0].decode("ascii")

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == "log":
                stack = cpu.reg_read(A.UC_ARM_REG_SP)
                args = [int.from_bytes(cpu.mem_read(stack + 4*i, 4), "little")
                        for i in range(3)]
                seen.append((name, r0, string(r1), r2, string(r3),
                             *(string(arg) for arg in args)))
                cpu.emu_stop()
            else:
                seen.append((name, r0, r1))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols["audio_uart_page_43f09a"] if compiled else 0x43f09a) | 1,
                     0x600000, count=300)
        return seen

    cases = 0
    for object_ in (0, 0x20000120, 0x20000abc):
        for x in (0, 1, 0xffffffff, 0x12345678):
            for y in (0, 1, 0x80000000, 0xfedcba98):
                native = run(False, object_, x, y)
                candidate = run(True, object_, x, y)
                assert native == candidate, (object_, x, y, native, candidate)
                cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_OBJ_SET_POS_43F09A",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": IMAGE_SHA, "native_body_sha256": BODY_SHA,
           "cases": cases, "null_assertion_cases": 16,
           "limits": ["The X and Y child setters remain separate provider bodies.",
                      "Null cases compare logger arguments before the deliberate invalid write.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
