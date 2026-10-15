#!/usr/bin/env python3
"""Compare Apollo font-chain glyph descriptor C with native code."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_font_glyph_describe_4d56c0.c"
OUT=G2/"build/c-firmware/20261015/main-page-font-glyph-describe-4d56c0"
SHIM='''#include <stdint.h>
void audio_uart_font_resource_enter_46f65e(void){}
void audio_uart_font_resource_leave_46f674(void){}
uint32_t glyph_cb(const void*f,void*d,uint32_t g,uint32_t n)
{(void)f;(void)d;(void)g;(void)n;return 0;}
'''
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get(c,a):return int.from_bytes(c.mem_read(a,4),"little")
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_font_glyph_describe_4d56c0",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            first,second,flag1,flag2,chain,disable_next,high_resource=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            node1,node2,out=0x20011000,0x20011100,0x20012000
            callback=syms["glyph_cb"]|1
            for node,disabled in ((node1,disable_next),(node2,0)):
                c.mem_write(node,bytes([0x55])*0x30)
                put(c,node,callback)
                put(c,node+0xc,0x12345678)
                c.mem_write(node+0x14,bytes([4 if disabled else 0]))
                put(c,node+0x18,0x80000001 if high_resource else 0)
            put(c,node1+0x1c,node2 if chain else 0)
            put(c,node2+0x1c,0)
            c.mem_write(out,bytes([0xa5])*32)
            cb=syms["glyph_cb"]
            enter=syms["audio_uart_font_resource_enter_46f65e"] if compiled else 0x46f65e
            leave=syms["audio_uart_font_resource_leave_46f674"] if compiled else 0x46f674
            trace=[]
            def hook(cpu,address,size,_):
                r0,r1,r2,r3=(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if address==(cb&~1):
                    node=1 if r0==node1 else 2
                    ordinal=sum(x[0]=="cb" and x[1]==node for x in trace)
                    found,provisional=(first,flag1) if node==1 else (second,flag2)
                    trace.append(("cb",node,r2,r3,ordinal))
                    cpu.mem_write(r1+4,bytes([0x20+node]))
                    cpu.mem_write(r1+0xf,bytes([1 if provisional else 0]))
                    cpu.reg_write(A.UC_ARM_REG_R0,found)
                elif address==(enter&~1):
                    trace.append(("enter",))
                elif address==(leave&~1):
                    trace.append(("leave",))
                else:return
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            for reg,value in ((A.UC_ARM_REG_R0,node1),(A.UC_ARM_REG_R1,out),
                              (A.UC_ARM_REG_R2,65),(A.UC_ARM_REG_R3,66),
                              (A.UC_ARM_REG_SP,0x203ff000),(A.UC_ARM_REG_LR,0x600001)):
                c.reg_write(reg,value)
            entry=syms["audio_uart_font_glyph_describe_4d56c0"] if compiled else 0x4d56c0
            c.emu_start(entry|1,0x600000,count=100000)
            result=bytearray(c.mem_read(out,32))
            ptr=int.from_bytes(result[:4],"little")
            result[:4]=(0 if ptr==0 else 1 if ptr==node1 else 2 if ptr==node2 else 3).to_bytes(4,"little")
            return trace,c.reg_read(A.UC_ARM_REG_R0),bytes(result)
        cases=list(itertools.product((0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_DESCRIBE_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x4d56c0..0x4d57f3",
             "cases":len(cases),"limits":["Font callbacks and resource guards are controlled; null assertions, corrupt font chains, and live font rendering remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
