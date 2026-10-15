#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo page selection traversal."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_update_core_44d63a.c"
OUT = G2 / "build/c-firmware/20261015/main-page-update-core-44d63a"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *p,uint32_t bit){return 0;}
void *audio_uart_page_overlay_44dca2(const void *p){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t code,void *arg){return 1;}
void audio_uart_display_size_changed(void *p){}
void *audio_uart_page_context_find_44d77a(void *p){return 0;}
'''
LOWER = [("flag", 0x43e0e0, "audio_uart_lv_obj_has_flag_43e0e0"),
         ("overlay", 0x44dca2, "audio_uart_page_overlay_44dca2"),
         ("event", 0x451670, "audio_uart_lv_obj_event_451670"),
         ("invalidate", 0x440656, "audio_uart_display_size_changed"),
         ("context", 0x44d77a, "audio_uart_page_context_find_44d77a")]


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_update_core_44d63a",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, flags, current, first, next_node, state, event_result, callback):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, node_a, node_b = 0x20010000, 0x20012000, 0x20012020
            obj_a, obj_b = 0x20013000, 0x20013100
            callback_addr, first_addr, next_addr, user_addr = (
                0x20019000, 0x20018000, 0x20018100, 0x20018200)
            data = bytearray(64)
            data[0x0c:0x10] = ([0, node_a, node_b][current]).to_bytes(4, "little")
            data[0x10:0x14] = ((callback_addr | 1) if callback else 0).to_bytes(4, "little")
            data[0x1c] = flags
            u.mem_write(page, bytes(data))
            for node, obj in ((node_a, obj_a), (node_b, obj_b)):
                u.mem_write(node, obj.to_bytes(4, "little") + b"\0" * 28)
                o = bytearray(64)
                o[0x28:0x2a] = state.to_bytes(2, "little")
                u.mem_write(obj, bytes(o))
            cuts = {(syms[name] & ~1) if compiled else addr: label
                    for label, addr, name in LOWER}
            cuts.update({first_addr: "first", next_addr: "next", callback_addr: "callback",
                         user_addr: "user"})
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1, r2 = (cpu.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if len(trace) >= 64:
                    raise RuntimeError("oracle case did not converge")
                trace.append((op, r0, r1 if op in ("event", "flag", "next") else 0))
                result = {"first": node_a if first else 0,
                          "next": node_b if next_node and r1 == node_a else 0,
                          "flag": 0, "overlay": 0, "context": user_addr,
                          "event": event_result}.get(op, 0)
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_R1, first_addr | 1)
            u.reg_write(A.UC_ARM_REG_R2, next_addr | 1)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_update_core_44d63a"] if compiled else 0x44d63a
            u.emu_start(entry | 1, 0x600000, count=100000)
            return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(page, 64))

        cases = []
        for flags in (0, 1, 8):
            for current, first, next_node in ((0, 0, 0), (0, 1, 0), (1, 1, 0),
                                              (1, 1, 1)):
                for state, event_result, callback in ((0, 1, 0), (0, 1, 1),
                                                      (0, 0, 1), (0x80, 1, 1)):
                    cases.append((flags, current, first, next_node,
                                  state, event_result, callback))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[:2], source[:2], native[2] == source[2]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_CORE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d63a..0x44d779",
               "cases": len(cases),
               "limits": ["Traversal callbacks and five lower providers are controlled.",
                          "Native low-word return, lower-call trace, and 64-byte page state are compared.",
                          "Full object/event semantics and hardware remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()
