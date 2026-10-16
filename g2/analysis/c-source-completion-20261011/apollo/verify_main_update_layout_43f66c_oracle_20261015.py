#!/usr/bin/env python3
"""Compare the native LV layout outer loop with controlled recursive effects."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_update_layout_43f66c.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY_SHA = "b83933a76976dd96b902ce608d450efcc6a633e1187acb1144bbd34ed743f06f"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
assert hashlib.sha256(IMAGE[0x43f66c-0x438000:0x43f6ac-0x438000]).hexdigest() == BODY_SHA
OUT = G2 / "build/c-firmware/20261015/main-update-layout-43f66c"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x100];
__attribute__((naked)) void *audio_uart_lv_object_screen(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_update_layout_440d70(void*a){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43f66c",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, busy, screen_flags, rearm, object_):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        root = symbols["audio_uart_display_lv_root"] if compiled else 0x2006f548
        screen = 0x20003000
        uc.mem_write(root + 0x60, bytes([busy]))
        uc.mem_write(screen + 0x2a, screen_flags.to_bytes(2, "little"))
        for reg, word in ((A.UC_ARM_REG_R0, object_), (A.UC_ARM_REG_SP, 0x200ff000),
                          (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, word)
        hooks = ({0x44dbc4: "screen", 0x440d70: "update"} if not compiled else {
            symbols["audio_uart_lv_object_screen"] & ~1: "screen",
            symbols["audio_uart_lv_obj_update_layout_440d70"] & ~1: "update"})
        seen = []
        updates = 0

        def observe(cpu, address, size, _):
            nonlocal updates
            name = hooks.get(address)
            if name is None:
                return
            seen.append((name, cpu.reg_read(A.UC_ARM_REG_R0)))
            if name == "screen":
                cpu.reg_write(A.UC_ARM_REG_R0, screen)
            else:
                updates += 1
                if updates <= rearm:
                    flags = int.from_bytes(cpu.mem_read(screen + 0x2a, 2), "little")
                    cpu.mem_write(screen + 0x2a, (flags | 4).to_bytes(2, "little"))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols["audio_uart_page_43f66c"] if compiled else 0x43f66c) | 1,
                     0x600000, count=500)
        return (seen, uc.mem_read(root + 0x60, 1)[0],
                int.from_bytes(uc.mem_read(screen + 0x2a, 2), "little"))

    cases = 0
    for busy in (0, 1, 2):
        for screen_flags in (0, 4, 0x104):
            for rearm in (0, 1):
                for object_ in (0x20004000, 0x20005000):
                    native = run(False, busy, screen_flags, rearm, object_)
                    candidate = run(True, busy, screen_flags, rearm, object_)
                    assert native == candidate, (busy, screen_flags, rearm,
                                                 object_, native, candidate)
                    cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_UPDATE_LAYOUT_43F66C",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": IMAGE_SHA, "native_body_sha256": BODY_SHA,
           "cases": cases,
           "limits": ["The recursive child at 0x440d70 is a separate provider gate.",
                      "Screen lookup and recursive dirty-bit effects were controlled hooks.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
