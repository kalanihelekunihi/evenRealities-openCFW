#!/usr/bin/env python3
"""Compare recursive LV layout traversal and dirty-bit child calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_update_layout_recursive_440d70.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY_SHA = "b7ab4305a7cc20a086a8df4692719b7d71432e3a4e7ef5edbacea1d3c75730c1"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
assert hashlib.sha256(IMAGE[0x440d70-0x438000:0x440dda-0x438000]).hexdigest() == BODY_SHA
OUT = G2 / "build/c-firmware/20261015/main-update-layout-recursive-440d70"
OUT.mkdir(parents=True, exist_ok=True)
NATIVE_CHILDREN = {
    "count": 0x44ddea, "invalidate": 0x43f1a4, "refr_pos": 0x43ffd0,
    "layout": 0x4546f4, "scroll": 0x44f316,
}
SYMBOLS = {
    "count": "audio_uart_lv_child_count_44ddea",
    "invalidate": "audio_uart_lv_basic_invalidate_43f1a4",
    "refr_pos": "audio_uart_lv_obj_refr_pos_43ffd0",
    "layout": "audio_uart_lv_obj_layout_apply_4546f4",
    "scroll": "audio_uart_lv_obj_scroll_reconcile_44f316",
}

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_lv_child_count_44ddea(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_basic_invalidate_43f1a4(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_refr_pos_43ffd0(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_layout_apply_4546f4(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_scroll_reconcile_44f316(void*a,uint32_t b){__asm volatile("bx lr");}
''')
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_update_layout_440d70",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, children, parent_flags, child_flags):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        parent, spec, entries, child_a, child_b = (0x20001000, 0x20002000,
                                                   0x20003000, 0x20004000,
                                                   0x20005000)
        uc.mem_write(parent + 8, spec.to_bytes(4, "little"))
        uc.mem_write(spec, entries.to_bytes(4, "little"))
        uc.mem_write(entries, child_a.to_bytes(4, "little") +
                     child_b.to_bytes(4, "little"))
        for address, flags in ((parent, parent_flags), (child_a, child_flags),
                               (child_b, child_flags)):
            uc.mem_write(address + 0x2a, flags.to_bytes(2, "little"))
        uc.reg_write(A.UC_ARM_REG_R0, parent)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = ({address: name for name, address in NATIVE_CHILDREN.items()} if not compiled
                 else {symbols[SYMBOLS[name]] & ~1: name for name in NATIVE_CHILDREN})
        seen = []

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None:
                return
            obj = cpu.reg_read(A.UC_ARM_REG_R0)
            arg = cpu.reg_read(A.UC_ARM_REG_R1)
            seen.append((name, obj, arg if name == "scroll" else None))
            cpu.reg_write(A.UC_ARM_REG_R0, children if name == "count" and obj == parent else 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        uc.emu_start((symbols["audio_uart_lv_obj_update_layout_440d70"] if compiled
                      else 0x440d70) | 1, 0x600000, count=1000)
        flags = tuple(int.from_bytes(uc.mem_read(address + 0x2a, 2), "little")
                      for address in (parent, child_a, child_b))
        return seen, flags

    cases = 0
    for children in (0, 2):
        for parent_flags in (0, 1, 2, 3, 0x103):
            for child_flags in (0, 1, 2, 3):
                native = run(False, children, parent_flags, child_flags)
                candidate = run(True, children, parent_flags, child_flags)
                assert native == candidate, (children, parent_flags, child_flags,
                                             native, candidate)
                cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_UPDATE_LAYOUT_RECURSIVE_440D70",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": IMAGE_SHA, "native_body_sha256": BODY_SHA,
           "cases": cases,
           "limits": ["Child count and three deeper layout effects were controlled hooks.",
                      "The position, layout-apply, and scroll providers remain separate gates.",
                      "Final placement and hardware behavior remain unverified."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
