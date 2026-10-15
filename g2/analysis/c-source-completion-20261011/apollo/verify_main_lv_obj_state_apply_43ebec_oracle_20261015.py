#!/usr/bin/env python3
"""Compare Apollo object state transitions with controlled style providers."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_obj_state_apply_43ebec.c"
OUT=G2/"build/c-firmware/20261015/main-lv-obj-state-apply-43ebec"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_state_transition_kind_44c178(void *o,uint32_t a,uint32_t b){return 0;}
void audio_uart_display_size_changed(void *o){}
void audio_uart_lv_update_layer_44c50e(void *o){}
void *audio_uart_lv_heap_alloc(uint32_t n){return 0;}
void audio_uart_lv_heap_free(void *p){}
uint32_t audio_uart_lv_style_reference_43dce0(void *s,uint32_t p,void *r){return 0;}
void audio_uart_lv_state_property_refresh_44bfae(void *o,uint32_t p,uint32_t a,uint32_t b,void *e){}
void audio_uart_page_style_refresh_44bc8c(void *o,uint32_t p,uint32_t q){}
void audio_uart_lv_refresh_draw_452d42(void *o){}
'''
LOWER=[("kind",0x44c178,"audio_uart_lv_state_transition_kind_44c178"),
       ("invalidate",0x440656,"audio_uart_display_size_changed"),
       ("layer",0x44c50e,"audio_uart_lv_update_layer_44c50e"),
       ("alloc",0x44f730,"audio_uart_lv_heap_alloc"),
       ("free",0x44f758,"audio_uart_lv_heap_free"),
       ("reference",0x43dce0,"audio_uart_lv_style_reference_43dce0"),
       ("property",0x44bfae,"audio_uart_lv_state_property_refresh_44bfae"),
       ("refresh",0x44bc8c,"audio_uart_page_style_refresh_44bc8c"),
       ("draw",0x452d42,"audio_uart_lv_refresh_draw_452d42")]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(p,n):p[:4]=(n&0xffffffff).to_bytes(4,"little")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_obj_state_apply_43ebec",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,kind,style_count,next_state,raw_second):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            obj,records,definition,letters,scratch=(0x20010000,0x20011000,
                                                     0x20012000,0x20013000,0x20014000)
            o=bytearray(0x60);put32(memoryview(o)[0x0c:],records)
            o[0x28:0x2a]=(0).to_bytes(2,"little")
            o[0x2a:0x2c]=(style_count<<4).to_bytes(2,"little")
            c.mem_write(obj,bytes(o))
            r=bytearray(0x20)
            put32(memoryview(r)[0:],0x20016000);put32(memoryview(r)[4:],0x00010001)
            put32(memoryview(r)[8:],0x20016020);put32(memoryview(r)[12:],raw_second)
            c.mem_write(records,bytes(r))
            d=bytearray(0x20)
            for i,v in enumerate((letters,0x20015000,0x42,0x1234,0x5678)):
                put32(memoryview(d)[i*4:],v)
            c.mem_write(definition,bytes(d));c.mem_write(letters,b"ab\0")
            c.mem_write(scratch,bytes(0x280))
            cuts={(syms[symbol]&~1) if compiled else address:label
                  for label,address,symbol in LOWER}
            trace=[]
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in
                             (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                result=0
                if op=="kind":trace.append((op,r0,r1,r2));result=kind
                elif op=="alloc":trace.append((op,r0));result=scratch
                elif op=="reference":
                    cpu.mem_write(r2,definition.to_bytes(4,"little"))
                    trace.append((op,r0,r1));result=1
                elif op=="property":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    entry=int.from_bytes(cpu.mem_read(sp,4),"little")
                    trace.append((op,r0,r1,r2,r3,bytes(cpu.mem_read(entry,0x14))))
                elif op in ("refresh",):trace.append((op,r0,r1,r2))
                else:trace.append((op,r0))
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,obj)
            c.reg_write(A.UC_ARM_REG_R1,next_state)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_obj_state_apply_43ebec"] if compiled else 0x43ebec
            c.emu_start(entry|1,0x600000,count=100000)
            return (trace,bytes(c.mem_read(obj,0x60)),bytes(c.mem_read(scratch,0x280)))
        cases=[(kind,styles,state,second)
               for kind in (0,1,2,3) for styles in (0,1,2)
               for state in (0,1,3) for second in (0x00010002,0x00010001)]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                first=next(((i,a,b) for i,(a,b) in enumerate(zip(native[0],source[0])) if a!=b),None)
                raise AssertionError((case,len(native[0]),len(source[0]),first,
                                      [a==b for a,b in zip(native,source)]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_OBJ_STATE_APPLY_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,"native_span":"0x43ebec..0x43ee2b",
             "cases":len(cases),"controlled_provider_count":len(LOWER),
             "limits":["Transition kind, style reference, property refresh and allocation are controlled.",
                       "Unchanged, direct and refreshed states with up to two style records compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
