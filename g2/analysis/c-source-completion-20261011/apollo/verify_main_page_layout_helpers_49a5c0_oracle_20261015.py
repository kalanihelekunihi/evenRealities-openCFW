#!/usr/bin/env python3
"""Compare Apollo layout flag and animation-copy helpers with native code."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_layout_helpers_49a5c0.c"
OUT=G2/"build/c-firmware/20261015/main-page-layout-helpers-49a5c0"
SHIM='''#include <stdint.h>
int32_t audio_uart_page_metric_499360(void*p,uint32_t s){(void)p;(void)s;return 0;}
int32_t audio_uart_page_metric_49936a(void*p,uint32_t s){(void)p;(void)s;return 0;}
'''
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_layout_copy_anim_49a5c0",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            kind,a,b,cval,d=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            dest,src=0x20011000,0x20012000
            cpu.mem_write(dest,bytes([0xa5])*0x100)
            cpu.mem_write(src,bytes([0x55])*0x100)
            trace=[]
            if kind=="copy":
                put(cpu,dest+0x34,b)
                for offset,value in ((0x34,0x1034),(0x44,0x1044),(0x40,0x1040),
                                     (0x10,0x1010),(0x38,0x1038)):
                    put(cpu,src+offset,value)
                args=(dest,src,a,0)
                entry=syms["audio_uart_page_layout_copy_anim_49a5c0"] if compiled else 0x49a5c0
            else:
                cpu.mem_write(dest+0x5c,bytes([a]))
                cpu.mem_write(dest+0x2b,bytes([b]))
                args=(dest,0x11111111,0x22222222,0x33333333)
                entry=syms["audio_uart_page_layout_flags_49abea"] if compiled else 0x49abea
                first=syms["audio_uart_page_metric_499360"] if compiled else 0x499360
                second=syms["audio_uart_page_metric_49936a"] if compiled else 0x49936a
                def hook(cpu,address,size,_):
                    if address==(first&~1):
                        trace.append(("first",cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
                        cpu.reg_write(A.UC_ARM_REG_R0,cval)
                    elif address==(second&~1):
                        trace.append(("second",cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
                        cpu.reg_write(A.UC_ARM_REG_R0,d)
                    else:return
                    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
                cpu.hook_add(UC_HOOK_CODE,hook)
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3),args):
                cpu.reg_write(reg,value)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            cpu.emu_start(entry|1,0x600000,count=10000)
            if kind=="copy":return bytes(cpu.mem_read(dest,0x80))
            return trace,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
        cases=[("copy",mode,initial,0,0) for mode,initial in itertools.product(
            (0,1,2,3,4,0xff),(0,1,0xffffffff,0x7fffffff))]
        cases += [("flags",flag,bit,width,height) for flag,bit,width,height in itertools.product(
            (0,0x20,0x40,0x60,0x80,0xff),(0,8),(0,0x3fffffff),(0,0x1fffffff))]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_HELPERS_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,
             "native_spans":["0x49a5c0..0x49a601","0x49abea..0x49ac49"],
             "cases":len(cases),"limits":["Style metric getters are controlled for flags; full layout update and live page state remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
