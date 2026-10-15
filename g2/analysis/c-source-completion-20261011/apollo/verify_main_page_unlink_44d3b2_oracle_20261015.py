#!/usr/bin/env python3
"""Controlled native/C Apollo page unlink comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_unlink_44d3b2.c"
OUT = G2 / "build/c-firmware/20261015/main-page-unlink-44d3b2"
SHIM = '''#include <stdint.h>
void *audio_uart_lv_list_first(void *p){return 0;}
void *audio_uart_lv_list_next(void *p,void *n){return 0;}
void *audio_uart_lv_list_first_482ce4(void *p){return 0;}
void audio_uart_lv_list_remove_482c0e(void *p,void *n){}
void audio_uart_lv_heap_free(void *p){}
void *audio_uart_page_context_find_44d77a(void *p){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t c,void *a){return 1;}
void audio_uart_page_notify_44d5f8(void *p){}
'''
LOWER = [("first", 0x482cd8, "audio_uart_lv_list_first"),
         ("next", 0x482cf0, "audio_uart_lv_list_next"),
         ("tail", 0x482ce4, "audio_uart_lv_list_first_482ce4"),
         ("remove", 0x482c0e, "audio_uart_lv_list_remove_482c0e"),
         ("free", 0x44f758, "audio_uart_lv_heap_free"),
         ("context", 0x44d77a, "audio_uart_page_context_find_44d77a"),
         ("event", 0x451670, "audio_uart_lv_obj_event_451670"),
         ("notify", 0x44d5f8, "audio_uart_page_notify_44d5f8")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_unlink_44d3b2",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, has_layer, has_context, active, head, tail, target, flags):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, layer, context = 0x20010000, 0x20011000, 0x20012000
            node_a, node_b = 0x20013000, 0x20013020
            p, l, c = bytearray(64), bytearray(64), bytearray(64)
            p[8:12] = (layer if has_layer else 0).to_bytes(4, "little")
            l[4:8] = (context if has_context else 0).to_bytes(4, "little")
            c[0xc:0x10] = ([0, node_a, node_b][active]).to_bytes(4, "little")
            c[0x1c] = flags
            u.mem_write(page, bytes(p))
            u.mem_write(layer, bytes(l))
            u.mem_write(context, bytes(c))
            u.mem_write(node_a, (page if target else page+4).to_bytes(4,"little")+b"\0"*28)
            u.mem_write(node_b, page.to_bytes(4,"little")+b"\0"*28)
            cuts = {(syms[name] & ~1) if compiled else addr: label
                    for label, addr, name in LOWER}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((op, r0, r1 if op in ("next", "remove", "event") else 0))
                result = {"first": node_a if head else 0,
                          "tail": node_a if tail else node_b,
                          "next": node_b if r1 == node_a else 0,
                          "context": context, "event": 1}.get(op, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_unlink_44d3b2"] if compiled else 0x44d3b2
            u.emu_start(entry | 1, 0x600000, count=100000)
            return trace, bytes(u.mem_read(page,64)), bytes(u.mem_read(layer,64)), \
                bytes(u.mem_read(context,64))

        cases = list(itertools.product((0,1), (0,1), (0,1,2), (0,1), (0,1),
                                       (0,1), (0,1,8,9)))
        for case in cases:
            native, source = run(False,*case), run(True,*case)
            if native != source:
                raise AssertionError((case,native[0],source[0],
                                      [a==b for a,b in zip(native[1:],source[1:])]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_UNLINK_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d3b2..0x44d45b",
               "cases": len(cases),
               "limits": ["Eight lower providers are controlled; page, layer, context and call trace compared.",
                          "Null-page fatal path, allocator effects and hardware are unverified."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__ == "__main__":
    main()
