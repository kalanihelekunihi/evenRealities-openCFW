#!/usr/bin/env python3
"""Native/C controlled call-order comparison for page-tree initialization."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_initialize_44d0f0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-initialize-44d0f0"
LOWER = {
    "prepare": (0x43f648, "audio_uart_lv_mark_layout_43f648"),
    "lock": (0x44bde0, "audio_uart_page_lock_44bde0"),
    "visit": (0x482f8a, "audio_uart_lv_theme_apply_482f8a"),
    "descriptor": (0x44d1fc, "audio_uart_page_descriptor_init_44d1fc"),
    "flags": (0x44bc8c, "audio_uart_page_style_refresh_44bc8c"),
    "relayout": (0x43ffa0, "audio_uart_page_relayout_43ffa0"),
    "context": (0x44d33a, "audio_uart_page_context_44d33a"),
    "needs": (0x44d1cc, "audio_uart_page_needs_context_44d1cc"),
    "attach": (0x44d342, "audio_uart_page_attach_context_44d342"),
    "overlay": (0x44dca2, "audio_uart_page_overlay_44dca2"),
    "event": (0x451670, "audio_uart_lv_obj_event_451670"),
    "finalize": (0x440656, "audio_uart_display_size_changed"),
}
SHIM = '''#include <stdint.h>
void audio_uart_lv_mark_layout_43f648(void*a){}
void audio_uart_page_lock_44bde0(uint32_t a){}
void audio_uart_lv_theme_apply_482f8a(void*a){}
void audio_uart_page_descriptor_init_44d1fc(const void*a,void*b){}
void audio_uart_page_style_refresh_44bc8c(void*a,uint32_t b,uint32_t c){}
void audio_uart_page_relayout_43ffa0(void*a){}
void *audio_uart_page_context_44d33a(void){return 0;}
uint32_t audio_uart_page_needs_context_44d1cc(void*a){return 0;}
void audio_uart_page_attach_context_44d342(void*a,void*b){}
void *audio_uart_page_overlay_44dca2(void*a){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void*a,uint32_t b,void*c){return 0;}
void audio_uart_display_size_changed(void*a){}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_initialize_44d0f0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, present, context, needs, overlay):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page = 0x20010000 if present else 0
            u.mem_write(0x20010000, (0x756108).to_bytes(4, "little") + b"\x33" * 124)
            cuts = {(syms[symbol] & ~1) if compiled else addr: op
                    for op, (addr, symbol) in LOWER.items()}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if op == "descriptor":
                    trace.append((op, r0, r1))
                elif op == "flags":
                    trace.append((op, r0, r1, r2))
                elif op in ("attach", "event"):
                    trace.append((op, r0, r1, r2 if op == "event" else None))
                else:
                    trace.append((op, r0))
                if op == "context":
                    cpu.reg_write(A.UC_ARM_REG_R0, 0x20011000 if context else 0)
                elif op == "needs":
                    cpu.reg_write(A.UC_ARM_REG_R0, int(needs))
                elif op == "overlay":
                    cpu.reg_write(A.UC_ARM_REG_R0, 0x20012000 if overlay else 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_initialize_44d0f0"] if compiled else 0x44d0f0
            u.emu_start(entry | 1, 0x600000, count=100000)
            return trace, bytes(u.mem_read(0x20010000, 128))

        cases = 0
        for present, context, needs, overlay in itertools.product((0, 1), repeat=4):
            native = run(False, present, context, needs, overlay)
            source = run(True, present, context, needs, overlay)
            if native != source:
                raise AssertionError((present, context, needs, overlay, native, source))
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_INITIALIZE_44D0F0_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44d0f0..0x44d16d",
               "cases": cases,
               "limits": ["Twelve child calls are controlled at their native interfaces.",
                          "Call order, arguments, and page memory are compared.",
                          "Full page-tree behavior and hardware layout remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)


if __name__ == "__main__":
    main()
