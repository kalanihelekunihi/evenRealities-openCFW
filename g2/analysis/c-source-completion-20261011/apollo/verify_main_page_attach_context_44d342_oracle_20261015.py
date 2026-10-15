#!/usr/bin/env python3
"""Controlled native/C page context attachment normal-path comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_attach_context_44d342.c"
OUT = G2 / "build/c-firmware/20261015/main-page-attach-context-44d342"
LOWER = {
    "unlink": (0x44d3b2, "audio_uart_page_unlink_44d3b2"),
    "layer": (0x43e1fa, "audio_uart_lv_obj_setup_layer_43e1fa"),
    "append": (0x482bca, "audio_uart_font_path_node_append"),
    "first": (0x482cd8, "audio_uart_lv_list_first"),
    "notify": (0x44d5f8, "audio_uart_page_notify_44d5f8"),
}
SHIM = '''#include <stdint.h>
void audio_uart_page_unlink_44d3b2(void*a){}
void audio_uart_lv_obj_setup_layer_43e1fa(void*a){}
void *audio_uart_font_path_node_append(void*a){return 0;}
void *audio_uart_lv_list_first(void*a){return 0;}
void audio_uart_page_notify_44d5f8(void*a){}
void audio_uart_lvgl_log(uint32_t level,const char *source,uint32_t line,const char *name,...){}
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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_attach_context_44d342",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, present, has_layer, first_matches):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, context, layer, node = 0x20010000, 0x20012000, 0x20013000, 0x20014000
            initial_page = bytearray(b"\x33" * 64)
            initial_page[8:12] = (layer if has_layer else 0).to_bytes(4, "little")
            u.mem_write(page, bytes(initial_page))
            u.mem_write(layer, b"\x44" * 64)
            u.mem_write(node, b"\x55" * 32)
            cuts = {(syms[symbol] & ~1) if compiled else addr: op
                    for op, (addr, symbol) in LOWER.items()}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append((op, r0))
                if op == "layer":
                    cpu.mem_write(page+8, layer.to_bytes(4, "little"))
                elif op == "append":
                    cpu.reg_write(A.UC_ARM_REG_R0, node)
                elif op == "first":
                    cpu.reg_write(A.UC_ARM_REG_R0, node if first_matches else node+8)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, context if present else 0)
            u.reg_write(A.UC_ARM_REG_R1, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_attach_context_44d342"] if compiled else 0x44d342
            u.emu_start(entry | 1, 0x600000, count=100000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(page, 64)),
                    bytes(u.mem_read(layer, 64)), bytes(u.mem_read(node, 32)))

        count = 0
        for present, has_layer, first_matches in itertools.product((0, 1), repeat=3):
            native = run(False, present, has_layer, first_matches)
            source = run(True, present, has_layer, first_matches)
            if native != source:
                raise AssertionError((present, has_layer, first_matches,
                                      native[:2], source[:2],
                                      [a == b for a, b in zip(native[2:], source[2:])]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_ATTACH_CONTEXT_44D342_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44d342..0x44d3b1",
               "cases": count,
               "limits": ["List-allocation failure and native fatal diagnostics are unverified.",
                          "Five lower calls are controlled; page, layer, node, and return are compared."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
