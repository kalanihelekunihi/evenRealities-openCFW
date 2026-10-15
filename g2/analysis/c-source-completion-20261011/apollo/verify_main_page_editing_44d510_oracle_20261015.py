#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo page editing state."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_editing_44d510.c"
OUT = G2 / "build/c-firmware/20261015/main-page-editing-44d510"
SHIM = '''#include <stdint.h>
void *audio_uart_page_context_find_44d77a(void *p){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t c,void *a){return 1;}
void audio_uart_display_size_changed(void *p){}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
'''
FUNCTIONS = [("set", 0x44d510, "audio_uart_page_set_editing_44d510"),
             ("active", 0x44d58c, "audio_uart_page_active_object_44d58c"),
             ("get", 0x44d5a4, "audio_uart_page_get_editing_44d5a4")]
LOWER = [("context", 0x44d77a, "audio_uart_page_context_find_44d77a"),
         ("event", 0x451670, "audio_uart_lv_obj_event_451670"),
         ("invalidate", 0x440656, "audio_uart_display_size_changed"),
         ("log", 0x44d25c, "audio_uart_lvgl_log")]


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_set_editing_44d510",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, function, present, flags, selected, requested, event_result):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, node, obj, context = 0x20010000, 0x20012000, 0x20013000, 0x20014000
            data = bytearray(64)
            data[0x0c:0x10] = (node if selected else 0).to_bytes(4,"little")
            data[0x1c] = flags
            u.mem_write(page, bytes(data))
            u.mem_write(node, obj.to_bytes(4,"little")+b"\0"*28)
            cuts = {(syms[name] & ~1) if compiled else addr: label
                    for label, addr, name in LOWER}
            trace = []

            def read_string(ptr):
                return bytes(u.mem_read(ptr, 128)).split(b"\0",1)[0].decode("utf8","replace")

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0,r1,r2,r3 = (cpu.reg_read(r) for r in
                               (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if op == "log":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    stack = [int.from_bytes(cpu.mem_read(sp+4*i,4),"little") for i in range(3)]
                    trace.append((op,r0,read_string(r1),r2,read_string(r3),
                                  *[read_string(p) for p in stack]))
                    cpu.emu_stop()
                    return
                trace.append((op,r0,r1 if op == "event" else 0,
                              r2 if op == "event" else 0))
                cpu.reg_write(A.UC_ARM_REG_R0,
                              context if op == "context" else event_result if op == "event" else 0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,page if present else 0)
            u.reg_write(A.UC_ARM_REG_R1,requested)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            _,native_entry,name = next(row for row in FUNCTIONS if row[0] == function)
            u.emu_start((syms[name] if compiled else native_entry)|1,0x600000,count=100000)
            return (u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(page,64)))

        cases = []
        for function in ("set","active","get"):
            for present,flags,selected,requested,event_result in itertools.product(
                    (0,1),(0,2,4,0xff),(0,1),(0,1,0x100),(0,1,0x101)):
                if not present and function == "set":
                    cases.append((function,present,flags,selected,requested,event_result))
                elif present or function != "set":
                    cases.append((function,present,flags,selected,requested,event_result))
        for case in cases:
            native, source = run(False,*case),run(True,*case)
            if native != source:
                raise AssertionError((case,native[:2],source[:2],native[2]==source[2]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_EDITING_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_spans":["0x44d510..0x44d58b",
             "0x44d58c..0x44d5a3","0x44d5a4..0x44d5b7"],"cases":len(cases),
             "limits":["Null setter stops at logger entry; logger internals and loop are not executed.",
                       "Context, event and invalidation lower calls are controlled."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":
    main()
