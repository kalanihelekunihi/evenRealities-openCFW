#!/usr/bin/env python3
"""Compare the native bounded object-style lookup and property adapter."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_page_style_get_44beaa.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_page_style_get_44beaa": (0x44beaa, 0x44bef2,
        "214aab7d6730ee19594135e0aa8533eb1f8ff0f02d00567304c245d89064a4ae"),
    "audio_uart_lv_style_get_482946": (0x482946, 0x482950,
        "152db6bc74bffc0424ceeb1dc3eeaffabef107ac09a125bfbfc4c0093ccfb7af"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-page-style-get-44beaa"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_lv_style_lookup_482716(const void*a,uint32_t b,uint32_t*c){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_style_get_44beaa",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, count, rows, property_, selector, result):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        root, table, out = 0x20001000, 0x20002000, 0x20004000
        uc.mem_write(root + 0x0c, table.to_bytes(4, "little"))
        uc.mem_write(root + 0x2a, (count << 4).to_bytes(2, "little"))
        for index, (style, descriptor) in enumerate(rows):
            uc.mem_write(table + index*8, style.to_bytes(4, "little") +
                         descriptor.to_bytes(4, "little"))
        uc.mem_write(out, (0xfeedface).to_bytes(4, "little"))
        args = ((root, property_, out, selector) if entry == "audio_uart_page_style_get_44beaa"
                else (0x20003000, property_, out, selector))
        for reg, word in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3), args):
            uc.reg_write(reg, word)
        uc.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        target = symbols["audio_uart_lv_style_lookup_482716"] & ~1 if compiled else 0x482716
        calls = []

        def observe(cpu, address, size, _):
            if address != target:
                return
            calls.append(tuple(cpu.reg_read(reg) for reg in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)))
            cpu.mem_write(out, (0xabcdef01).to_bytes(4, "little"))
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x600000, count=500)
        return calls, uc.reg_read(A.UC_ARM_REG_R0), int.from_bytes(uc.mem_read(out, 4), "little")

    cases = 0
    patterns = [[], [(0x20003000, 0x01000123)],
                [(0x20003000, 0x00000123)],
                [(0x20003000, 0x01000040), (0x20003010, 0x01000123)],
                [(0x20003000, 0x01000123), (0x20003010, 0x01000123)],
                [(0x20003000, 0xff000123)]]
    for entry in BODIES:
        for rows in (patterns if entry == "audio_uart_page_style_get_44beaa" else [[]]):
            for count in ((0, len(rows)) if rows else (0,)):
                for property_ in (8, 0x109):
                    for selector in (0x123, 0x1000123):
                        for result in (0, 1, 2):
                            native = run(False, entry, count, rows, property_, selector, result)
                            candidate = run(True, entry, count, rows, property_, selector, result)
                            assert native == candidate, (entry, count, rows, property_,
                                                         selector, result, native, candidate)
                            cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_PAGE_STYLE_GET_44BEAA",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["The LV style lookup at 0x482716 remains a separate provider gate.",
                      "Controlled row/status cases do not prove final placement or hardware behavior."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
