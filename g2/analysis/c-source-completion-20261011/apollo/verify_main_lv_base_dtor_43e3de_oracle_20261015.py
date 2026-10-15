#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo base-object destructor."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_base_dtor_43e3de.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-dtor-43e3de"
PROVIDERS={'mark':('audio_uart_lv_style_mark_45028e',0x45028e),'lock':('audio_uart_page_lock_44bde0',0x44bde0),'theme':('audio_uart_lv_theme_refresh_44bc3a',0x44bc3a),'unlink':('audio_uart_lv_style_unlink_450500',0x450500),'group':('audio_uart_lv_obj_group_43e1be',0x43e1be),'detach':('audio_uart_page_unlink_44d3b2',0x44d3b2),'destroy':('audio_uart_lv_style_destroy_450228',0x450228),'free':('audio_uart_lv_heap_free',0x44f758)}
SHIM='''#include <stdint.h>
void audio_uart_lv_style_mark_45028e(void*p){(void)p;}
void audio_uart_page_lock_44bde0(uint32_t v){(void)v;}
void audio_uart_lv_theme_refresh_44bc3a(void*p){(void)p;}
uint32_t audio_uart_lv_style_unlink_450500(void*p,void*s){(void)p;(void)s;return 0;}
void *audio_uart_lv_obj_group_43e1be(void*p){(void)p;return 0;}
void audio_uart_page_unlink_44d3b2(void*p){(void)p;}
void audio_uart_lv_style_destroy_450228(void*p){(void)p;}
void audio_uart_lv_heap_free(void*p){(void)p;}
'''
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf";shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_base_dtor_43e3de",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            group_on,spec_on,first_on=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x400000)
            page,spec,first=0x20011000,0x20012000,0x20013000
            c.mem_write(page,bytes([0xa5])*0x80);c.mem_write(spec,bytes([0x55])*0x40)
            put(c,page+8,spec if spec_on else 0);put(c,spec,first if first_on else 0)
            targets={(syms[name] if compiled else native)&~1:op for op,(name,native) in PROVIDERS.items()}
            trace=[]
            def hook(c,address,size,_):
                op=targets.get(address)
                if op is None:return
                r0,r1=c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1)
                trace.append((op,r0,r1 if op=='unlink' else None))
                if op=='group':c.reg_write(A.UC_ARM_REG_R0,0x20014000 if group_on else 0)
                elif op=='unlink':c.reg_write(A.UC_ARM_REG_R0,0)
                c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,0x12345678);c.reg_write(A.UC_ARM_REG_R1,page)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((syms['audio_uart_lv_base_dtor_43e3de'] if compiled else 0x43e3de)|1,0x600000,count=10000)
            return trace,bytes(c.mem_read(page,0x20)),bytes(c.mem_read(spec,0x20))
        cases=list(itertools.product((0,1),repeat=3))
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_DTOR_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_span":"0x43e3de..0x43e441","cases":len(cases),"limits":["All eight lower calls are controlled; allocator effects, live styles and recursive object teardown remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt['status'],len(cases))
if __name__=='__main__':main()
