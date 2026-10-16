#!/usr/bin/env python3
"""Compare two bounded LV page setters with the official Apollo image."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_pair_43f6b8.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261015/main-page-pair-43f6b8"
OUT.mkdir(parents=True, exist_ok=True)
NATIVE = {"audio_uart_page_4411d4": 0x4411d4,
          "audio_uart_page_43f6b8": 0x43f6b8}
NATIVE_BODIES = {
    "audio_uart_page_4411d4": (0x4411d4, 0x4411e4,
                                "3d89696d92cb859542f864c6b2be546106c8b50f9fbf294fd9b93471e3e46da9"),
    "audio_uart_page_43f6b8": (0x43f6b8, 0x43f6d6,
                                "f55ca5ad1ac8828e95f6f2fd2964ce7df23499ef42df073b85afb9ef25f583f2"),
}
for start, end, expected in NATIVE_BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) void audio_uart_page_style_apply_44be4c(void*a,uint8_t b,uint32_t c,uint32_t d){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_43f09a(uint32_t a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43f6b8",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, obj, index, value, selector):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        for register, word in ((A.UC_ARM_REG_R0, obj), (A.UC_ARM_REG_R1, index),
                               (A.UC_ARM_REG_R2, value if entry.endswith("43f6b8") else selector),
                               (A.UC_ARM_REG_R3, selector),
                               (A.UC_ARM_REG_SP, 0x2000f000),
                               (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(register, word)
        hooks = {0x44be4c: "style", 0x43f09a: "second"} if not compiled else {
            symbols["audio_uart_page_style_apply_44be4c"] & ~1: "style",
            symbols["audio_uart_page_43f09a"] & ~1: "second"}
        seen = []

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            values = tuple(cpu.reg_read(reg) for reg in
                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                            A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            seen.append((name, values))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        address = symbols[entry] if compiled else NATIVE[entry]
        uc.emu_start(address | 1, 0x600000, count=200)
        return seen

    cases = []
    for entry in NATIVE:
        for obj in (0, 0x20000120):
            for index in (0, 9, 0xff, 0x1234):
                for value, selector in ((0, 0), (0xabcde, 3), (0xffffffff, 0x80000000)):
                    native = run(False, entry, obj, index, value, selector)
                    candidate = run(True, entry, obj, index, value, selector)
                    assert native == candidate, (entry, obj, index, value, selector,
                                                 native, candidate)
                    cases.append((entry, obj, index, value, selector))

receipt = {"status": "PASS_NATIVE_MAIN_PAGE_PAIR_43F6B8",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "cases": len(cases), "source_owned_symbols": sorted(NATIVE),
           "native_entries": {name: hex(address) for name, address in NATIVE.items()},
           "native_body_sha256": {name: body[2] for name, body in NATIVE_BODIES.items()},
           "limits": ["The second setter at 0x43f09a remains a separate provider gate.",
                      "Call trace comparisons do not prove final placement or hardware behavior."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
