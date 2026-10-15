#!/usr/bin/env python3
"""Compare stock scroll mode and top getters with C, including byte truncation."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_scroll_mode_top_44e2a4.c"
OUT=G2/"build/c-firmware/20261015/main-lv-scroll-mode-top-44e2a4"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void *p,uint32_t s,uint32_t id){return 0;}
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_scroll_mode_44e2a4",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,value,selector,present):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,spec=0x20010000,0x20011000
            u.mem_write(obj+8,(spec if present else 0).to_bytes(4,"little"))
            u.mem_write(spec+0x24,value.to_bytes(4,"little"))
            cut=(syms["audio_uart_lv_style_property_44bdea"]&~1) if compiled else 0x44bdea
            trace=[]
            def hook(cpu,address,size,unused):
                if address!=cut:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]
                trace.append(tuple(regs))
                cpu.reg_write(A.UC_ARM_REG_R0,value)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj)
            u.reg_write(A.UC_ARM_REG_R1,selector)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            name="audio_uart_lv_scroll_mode_44e2a4" if kind=="mode" else "audio_uart_lv_scroll_top_44e4aa"
            start=syms[name] if compiled else (0x44e2a4 if kind=="mode" else 0x44e4aa)
            u.emu_start(start|1,0x600000,count=100000)
            return trace,u.reg_read(A.UC_ARM_REG_R0)

        cases=list(itertools.product(("mode","top"),(0,1,0xff,0x100,0x80000000,0xffffffff),
                                     (0,1,0xffffffff),(False,True)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MODE_TOP_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_spans":["0x44e2a4..0x44e2af","0x44e4aa..0x44e4bb"],
             "cases":len(cases),"limits":["Style-property return controlled; no live object proof."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
