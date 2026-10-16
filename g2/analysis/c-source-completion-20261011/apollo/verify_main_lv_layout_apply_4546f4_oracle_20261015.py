#!/usr/bin/env python3
"""Native/C LV layout-ID and callback table dispatch comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_layout_apply_4546f4.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_lv_layout_id_4546d0": (0x4546d0, 0x4546dc,
        "e7db7bdbf8592de737b706de2eac46859b2626af4752fa4c086646562d6a4a8e"),
    "audio_uart_lv_obj_layout_apply_4546f4": (0x4546f4, 0x454730,
        "25316c1070fb5792e8274ea6bb6c0d88b8d6d27ede6f7e391bc904fdbb9b3eae"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-lv-layout-apply-4546f4"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x100];
__attribute__((naked)) uint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_layout_apply_4546f4",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, style_value, maximum, selector):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.mem_write(0x600100, b"\x70\x47")
        root = symbols["audio_uart_display_lv_root"] if compiled else 0x2006f548
        table, object_ = 0x20002000, 0x20004000
        uc.mem_write(root + 0x58, maximum.to_bytes(4, "little"))
        uc.mem_write(root + 0x5c, table.to_bytes(4, "little"))
        for i in range(256):
            uc.mem_write(table + i*8, (0x600101).to_bytes(4, "little") +
                         (0xabc00000 | i).to_bytes(4, "little"))
        for reg, word in ((A.UC_ARM_REG_R0, object_), (A.UC_ARM_REG_R1, selector),
                          (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x700001)):
            uc.reg_write(reg, word)
        prop_address = (symbols["audio_uart_lv_style_property_44bdea"] & ~1
                        if compiled else 0x44bdea)
        calls = []

        def observe(cpu, address, size, _):
            if address == prop_address:
                calls.append(("property", cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1),
                              cpu.reg_read(A.UC_ARM_REG_R2)))
                cpu.reg_write(A.UC_ARM_REG_R0, style_value)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            elif address == 0x600100:
                calls.append(("callback", cpu.reg_read(A.UC_ARM_REG_R0),
                              cpu.reg_read(A.UC_ARM_REG_R1)))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x700000, count=200)
        return calls, (uc.reg_read(A.UC_ARM_REG_R0)
                       if entry == "audio_uart_lv_layout_id_4546d0" else None)

    cases = 0
    values = (0, 1, 2, 3, 255, 0x10001, 0x12340002)
    for entry in BODIES:
        for style_value in values:
            for maximum in ((0, 1, 2, 255) if entry.endswith("4546f4") else (255,)):
                for selector in ((0,) if entry.endswith("4546f4") else (0, 3, 0xffffffff)):
                    native = run(False, entry, style_value, maximum, selector)
                    candidate = run(True, entry, style_value, maximum, selector)
                    assert native == candidate, (entry, style_value, maximum,
                                                 selector, native, candidate)
                    cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_LV_LAYOUT_APPLY_4546F4",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["The style-property result and callback side effects were controlled hooks.",
                      "The LV root layout registry is runtime data, not a final placement proof."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
