#!/usr/bin/env python3
"""Native/C scroll mode and reconciliation call-trace comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scroll_reconcile_44f316.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_lv_scroll_x_spec_mode_44e45a": (0x44e45a, 0x44e470,
        "08bb33cbc2a069e69c623e3da2ff2b1003fcd312db68e56662065bf15aca2c94"),
    "audio_uart_lv_scroll_y_spec_mode_44e470": (0x44e470, 0x44e486,
        "f05d5542aac5bc00db80e1c970305705be67cf9956fbc70f9ca51d01b5b48139"),
    "audio_uart_lv_obj_scroll_reconcile_44f316": (0x44f316, 0x44f3b8,
        "f5d644435517aee65c70805cf7787d175b1a99856115587a72afcb77c0632c31"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-lv-scroll-reconcile-44f316"
OUT.mkdir(parents=True, exist_ok=True)
CHILDREN = {
    "top": (0x44e4aa, "audio_uart_lv_scroll_top_44e4aa"),
    "bottom": (0x44e4bc, "audio_uart_lv_scroll_bottom_44e4bc"),
    "left": (0x44e586, "audio_uart_lv_scroll_left_44e586"),
    "right": (0x44e67a, "audio_uart_lv_scroll_right_44e67a"),
    "mode": (0x44e2a4, "audio_uart_lv_scroll_mode_44e2a4"),
    "dispatch": (0x44e884, "audio_uart_lv_scroll_dispatch_44e884"),
}

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) int32_t audio_uart_lv_scroll_top_44e4aa(void*a){__asm volatile("bx lr");}
__attribute__((naked)) int32_t audio_uart_lv_scroll_bottom_44e4bc(void*a){__asm volatile("bx lr");}
__attribute__((naked)) int32_t audio_uart_lv_scroll_left_44e586(void*a){__asm volatile("bx lr");}
__attribute__((naked)) int32_t audio_uart_lv_scroll_right_44e67a(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_scroll_mode_44e2a4(void*a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_scroll_dispatch_44e884(void*a,int32_t b,int32_t c,uint32_t d){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_scroll_reconcile_44f316",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, spec_flags, values, mode, animated):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        object_, spec = 0x20001000, 0x20002000
        uc.mem_write(object_ + 8, (spec if spec_flags is not None else 0).to_bytes(4, "little"))
        if spec_flags is not None:
            uc.mem_write(spec + 0x32, spec_flags.to_bytes(2, "little"))
        for reg, word in ((A.UC_ARM_REG_R0, object_),
                          (A.UC_ARM_REG_R1, animated),
                          (A.UC_ARM_REG_SP, 0x200ff000),
                          (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, word)
        hooks = ({native: name for name, (native, _) in CHILDREN.items()} if not compiled
                 else {symbols[symbol] & ~1: name for name, (_, symbol) in CHILDREN.items()})
        seen = []

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            args = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                          A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            seen.append((name, args if name == "dispatch" else args[:2] if name == "mode" else args[:1]))
            answer = mode if name == "mode" else values.get(name, 0)
            cpu.reg_write(A.UC_ARM_REG_R0, answer & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x600000, count=500)
        return (seen, uc.reg_read(A.UC_ARM_REG_R0)
                if entry != "audio_uart_lv_obj_scroll_reconcile_44f316" else None)

    cases = 0
    for entry in BODIES:
        if entry != "audio_uart_lv_obj_scroll_reconcile_44f316":
            for spec_flags in (None, 0, 4, 0x10, 0x3c, 0xffff):
                native = run(False, entry, spec_flags, {}, 0, 0)
                candidate = run(True, entry, spec_flags, {}, 0, 0)
                assert native == candidate, (entry, spec_flags, native, candidate)
                cases += 1
            continue
        tuples = ((0, 0, 0, 0), (1, -1, 1, -1), (5, -2, 5, -2),
                  (2, -5, 2, -5), (-1, -3, -1, 3), (1, 0, -2, 3),
                  (0x7fffffff, -0x80000000, -0x80000000, 0x7fffffff))
        for spec_flags in (None, 0, 4, 0x10, 0x14):
            for top, bottom, left, right in tuples:
                values = dict(top=top, bottom=bottom, left=left, right=right)
                for mode in (0, 1, 2):
                    for animated in (0, 1, 0x100):
                        native = run(False, entry, spec_flags, values, mode, animated)
                        candidate = run(True, entry, spec_flags, values, mode, animated)
                        assert native == candidate, (spec_flags, values, mode,
                                                     animated, native, candidate)
                        cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_LV_SCROLL_RECONCILE_44F316",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["Six lower scroll providers were controlled hooks.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
