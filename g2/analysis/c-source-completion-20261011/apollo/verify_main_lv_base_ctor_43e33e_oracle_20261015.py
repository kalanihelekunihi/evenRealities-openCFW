#!/usr/bin/env python3
"""Compare Apollo base-object constructor and metric wrappers with stock."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_base_ctor_43e33e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-ctor-43e33e"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_property_44bdea(void*p,uint32_t s,uint32_t n){(void)p;(void)s;(void)n;return 0;}
int32_t audio_uart_lv_scroll_left_44e586(void*p){(void)p;return 0;}
int32_t audio_uart_lv_scroll_top_44e4aa(void*p){(void)p;return 0;}
'''
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf";shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_base_ctor_43e33e",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            kind,parent_on,left,top,metric10,metric12,px,py,selector=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x400000)
            parent,child=0x20011000,0x20012000
            c.mem_write(parent,bytes([0x55])*0x100);c.mem_write(child,bytes([0xa5])*0x100)
            put(c,child+4,parent if parent_on else 0);put(c,parent+0x14,px);put(c,parent+0x18,py)
            native={'ctor':0x43e33e,'metric10':0x43dd86,'metric12':0x43dd90}
            source={'ctor':syms['audio_uart_lv_base_ctor_43e33e'],'metric10':syms['audio_uart_lv_metric_43dd86'],'metric12':syms['audio_uart_lv_metric_43dd90']}
            targets={((syms['audio_uart_lv_style_property_44bdea'] if compiled else 0x44bdea)&~1):'metric',((syms['audio_uart_lv_scroll_left_44e586'] if compiled else 0x44e586)&~1):'left',((syms['audio_uart_lv_scroll_top_44e4aa'] if compiled else 0x44e4aa)&~1):'top'}
            trace=[]
            def hook(c,address,size,_):
                op=targets.get(address)
                if op is None:return
                r0,r1,r2=(c.reg_read(reg) for reg in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
                trace.append((op,r0,r1 if op=='metric' else None,r2 if op=='metric' else None))
                result=(metric10 if r2==0x10 else metric12) if op=='metric' else (left if op=='left' else top)
                c.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,0x12345678 if kind=='ctor' else parent)
            c.reg_write(A.UC_ARM_REG_R1,child if kind=='ctor' else selector)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((source if compiled else native)[kind]|1,0x600000,count=10000)
            return trace,(bytes(c.mem_read(child,0x30)) if kind=='ctor' else c.reg_read(A.UC_ARM_REG_R0))
        cases=[('ctor',p,l,t,m10,m12,px,py,0) for p,l,t,m10,m12,px,py in itertools.product((0,1),(0,5,-3),(0,7,-2),(0,4,-1),(0,6,-4),(0,17),(0,23))]
        cases += [(k,1,0,0,v,v,0,0,s) for k,v,s in itertools.product(('metric10','metric12'),(0,7,-3),(0,1,0xffffffff))]
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_CTOR_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_spans":["0x43dd86..0x43dd99","0x43e33e..0x43e3dd"],"cases":len(cases),"limits":["Scroll and style-property providers are controlled; live parent state and base-class descriptor placement remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt['status'],len(cases))
if __name__=='__main__':main()
