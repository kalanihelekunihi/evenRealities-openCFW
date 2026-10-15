#!/usr/bin/env python3
"""Native/C call boundary comparison for six page metric selector wrappers."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_metric_getters_499360.c"
OUT=G2/"build/c-firmware/20261015/main-page-metric-getters-499360"
FUNCS=((0x499360,"audio_uart_page_metric_499360",1),
       (0x49936a,"audio_uart_page_metric_49936a",5),
       (0x499374,"audio_uart_page_metric_499374",7),
       (0x4993c0,"audio_uart_page_metric_4993c0",0x5a),
       (0x4993ca,"audio_uart_page_metric_4993ca",0x5b),
       (0x4993d4,"audio_uart_page_metric_4993d4",0x5c))
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void*p,uint32_t s,uint32_t n)
{(void)p;(void)s;(void)n;return 0;}
'''

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_metric_499360",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,func,page,selector,value):
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            target=syms["audio_uart_lv_style_property_44bdea"] if compiled else 0x44bdea
            trace=[]
            def hook(cpu,address,size,_):
                if address!=(target&~1):return
                trace.append(tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,
                    A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)))
                cpu.reg_write(A.UC_ARM_REG_R0,value)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,page)
            cpu.reg_write(A.UC_ARM_REG_R1,selector)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            native,sym,_=func
            cpu.emu_start((syms[sym] if compiled else native)|1,0x600000,count=10000)
            return trace,cpu.reg_read(A.UC_ARM_REG_R0)
        cases=list(itertools.product(FUNCS,(0,0x20010000),(0,0x12345678),
                                     (0,1,0x20014000,0xffffffff)))
        for case in cases:
            stock,source=run(False,*case),run(True,*case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_METRIC_GETTERS_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"functions":len(FUNCS),"cases":len(cases),
             "limits":["Style property provider is controlled; live style resolution remains a separate source contract."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
