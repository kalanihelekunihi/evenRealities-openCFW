#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo page class construction and disposal."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_class_lifecycle_49a0c0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-class-lifecycle-49a0c0"
HELPERS = (("mode", 0x43dfa4, "audio_uart_page_43dfa4"),
           ("layout", 0x499678, "audio_uart_page_layout_499678"),
           ("style", 0x49942e, "audio_uart_page_49942e"),
           ("free", 0x44f758, "audio_uart_lv_heap_free"))
SHIM = '''#include <stdint.h>
void audio_uart_page_43dfa4(void*p,uint32_t m){(void)p;(void)m;}
void audio_uart_page_layout_499678(void*p,uint32_t m){(void)p;(void)m;}
void audio_uart_page_49942e(void*p,const void*s){(void)p;(void)s;}
void audio_uart_lv_heap_free(void*p){(void)p;}
'''

def put32(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    if int.from_bytes(blob[0x49ab98-0x438000:0x49ab9c-0x438000],"little") != 0x78dc14:
        raise RuntimeError("page style literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td)/"shim.c", Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_class_ctor_49a0c0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
                if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, operation, seed, flags, pointer):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000)
            cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments: cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            page = 0x20012000
            cpu.mem_write(page,bytes(((seed+i*37)&255) for i in range(0x80)))
            cpu.mem_write(page+0x5c,bytes([flags]))
            put32(cpu,page+0x2c,pointer)
            targets = {(syms[sym]&~1) if compiled else addr:name
                       for name,addr,sym in HELPERS}
            trace=[]
            def hook(cpu,address,size,_):
                name=targets.get(address)
                if name is None:return
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append((name,r0,r1 if name!="free" else None))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,0x7561bc)
            cpu.reg_write(A.UC_ARM_REG_R1,page)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            key = "audio_uart_page_class_ctor_49a0c0" if operation=="ctor" else \
                  "audio_uart_page_class_dtor_49a150"
            entry = syms[key] if compiled else (0x49a0c0 if operation=="ctor" else 0x49a150)
            cpu.emu_start(entry|1,0x600000,count=100000)
            return trace, bytes(cpu.mem_read(page,0x80))

        cases = list(itertools.product(("ctor","dtor"),(0,0x5a,0xff),
                                       (0,0x10,0x70,0xff),(0,0x20014000)))
        for case in cases:
            native, source = run(False,*case), run(True,*case)
            if native != source:
                raise AssertionError((case,native[0],source[0],
                                      [(i,a,b) for i,(a,b) in enumerate(zip(native[1],source[1]))
                                       if a!=b][:12]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_CLASS_LIFECYCLE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,
             "native_spans":["0x49a0c0..0x49a12d","0x49a150..0x49a16d"],
             "cases":len(cases),
             "limits":["Page mode, layout, style, and heap-free helpers are controlled lower interfaces.",
                       "The style pointer is a stock ROM binding awaiting source-owned placement."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
