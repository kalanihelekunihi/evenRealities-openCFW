#!/usr/bin/env python3
"""Compare Apollo animation-list lookup with native code and controlled list cursor."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_lv_anim_lookup_450566.c"
OUT=G2/"build/c-firmware/20261015/main-page-lv-anim-lookup-450566"
SHIM='''#include <stdint.h>
uint8_t audio_uart_display_lv_state[0x200];
void*audio_uart_lv_list_first(void*l){(void)l;return 0;}
void*audio_uart_lv_list_next(void*l,void*n){(void)l;(void)n;return 0;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_lv_anim_lookup_450566",
                        str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            selectors,which,callback=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            nodes=[0x20011000+i*0x100 for i in range(len(selectors))]
            for i,(node,(var,func)) in enumerate(zip(nodes,selectors)):
                c.mem_write(node,bytes([0x55])*0x40)
                put(c,node,var);put(c,node+4,func)
            first=syms["audio_uart_lv_list_first"] if compiled else 0x482cd8
            next_fn=syms["audio_uart_lv_list_next"] if compiled else 0x482cf0
            root=(syms["audio_uart_display_lv_state"]+0xac) if compiled else 0x2006f5f4
            trace=[]
            def hook(cpu,address,size,_):
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                if address==(first&~1):
                    trace.append(("first",r0==root))
                    value=nodes[0] if nodes else 0
                elif address==(next_fn&~1):
                    index=nodes.index(r1) if r1 in nodes else -1
                    trace.append(("next",r0==root,index))
                    value=nodes[index+1] if 0<=index+1<len(nodes) else 0
                else:return
                cpu.reg_write(A.UC_ARM_REG_R0,value)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,which)
            c.reg_write(A.UC_ARM_REG_R1,callback)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_lv_anim_lookup_450566"] if compiled else 0x450566
            c.emu_start(entry|1,0x600000,count=10000)
            result=c.reg_read(A.UC_ARM_REG_R0)
            return trace,nodes.index(result)+1 if result in nodes else 0
        variants=((),((1,3),),((1,3),(2,4)),((2,4),(1,3)),
                  ((1,4),(1,3)),((2,4),(1,3),(1,4)))
        cases=list(itertools.product(variants,(1,2,3),(0,3,4,5)))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_LV_ANIM_LOOKUP_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x450566..0x4505a1",
             "cases":len(cases),"limits":["List traversal is controlled; live animation registry and mutation remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
