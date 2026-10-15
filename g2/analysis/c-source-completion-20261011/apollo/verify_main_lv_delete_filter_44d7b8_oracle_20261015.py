#!/usr/bin/env python3
"""Compare Apollo object deletion coordination with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_delete_event_filter_44d7b8.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-delete-filter-44d7b8"
SHIM = '''#include <stdint.h>
void audio_uart_display_size_changed(void *p){}
void *audio_uart_lv_obj_parent_44dca2(void *p){return 0;}
void *audio_uart_lv_display_for_object(void *p){return 0;}
void audio_uart_lv_child_delete_44df80(void *p){}
void audio_uart_lv_scrollbar_invalidate_44f2ca(void *p){}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t n,void *q){return 1;}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,... ){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_delete_event_filter_44d7b8",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        names = {
            "invalidate": (0x440656, "audio_uart_display_size_changed"),
            "parent": (0x44dca2, "audio_uart_lv_obj_parent_44dca2"),
            "display": (0x44dc0a, "audio_uart_lv_display_for_object"),
            "delete": (0x44df80, "audio_uart_lv_child_delete_44df80"),
            "scrollbar": (0x44f2ca, "audio_uart_lv_scrollbar_invalidate_44f2ca"),
            "event": (0x451670, "audio_uart_lv_obj_event_451670"),
            "log": (0x44d25c, "audio_uart_lvgl_log"),
        }
        def run(compiled, deleting, parented, display_present, current, parent_deleting):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            obj, parent, display = 0x20010000, 0x20011000, 0x20012000
            u.mem_write(obj + 0x2a, (0x1000 if deleting else 0).to_bytes(2, "little"))
            u.mem_write(parent + 0x2a, (0x1000 if parent_deleting else 0).to_bytes(2, "little"))
            u.mem_write(display + 0x2c4, (obj if current else parent).to_bytes(4, "little"))
            cuts = {(syms[name] & ~1) if compiled else address: kind
                    for kind, (address, name) in names.items()}
            trace = []
            def label(value):
                return {obj: "object", parent: "parent", display: "display", 0: "null"}.get(value, hex(value))
            def hook(cpu, address, size, user):
                kind = cuts.get(address)
                if kind is None: return
                r0, r1, r2 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if kind == "event": trace.append((kind, label(r0), r1, r2))
                elif kind == "log": trace.append((kind, r0, r2))
                else: trace.append((kind, label(r0)))
                result = (parent if parented else 0) if kind == "parent" else \
                         (display if display_present else 0) if kind == "display" else 1
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, obj)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_page_delete_event_filter_44d7b8"] if compiled else 0x44d7b8) | 1,
                        0x600000, count=100000)
            return trace, int.from_bytes(u.mem_read(display + 0x2c4, 4), "little")
        cases = list(itertools.product((False, True), repeat=5))
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DELETE_FILTER_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d7b8..0x44d877",
               "cases": len(cases),
               "limits": ["Object delete, event, invalidation, and log helpers controlled.",
                          "Log strings, null-object fault path, and live page transitions remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
