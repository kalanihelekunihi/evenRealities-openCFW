#!/usr/bin/env python3
"""Controlled whole-branch comparison for Apollo LV draw-task renderer."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_draw_task_render_451c6e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-draw-task-render-451c6e"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
void *audio_uart_lv_render_task_alloc_4843ee(void *l,const void *a){return 0;}
void *audio_uart_lv_malloc(uint32_t n){return 0;}
void audio_uart_lv_render_task_queue_484476(void *l,void *t){}
void audio_uart_lv_draw_descriptor_init_451c3a(void *d){}
void audio_uart_ambiq_image_options_init_488918(void *d){}
void audio_uart_lv_image_descriptor_init_489f5e(void *d){}
uint32_t audio_uart_lv_image_source_type_488cb8(const void *s){return 0;}
uint32_t audio_uart_lv_image_header_488f6a(const void *s,void *h){return 0;}
void audio_uart_page_event_calculate_489546(void *o,const char *t,const void *f,int32_t a,int32_t b,int32_t c,uint32_t d){}
void audio_uart_lv_area_transform_451082(const void *p,void *a,uint32_t s,uint32_t x,uint32_t y){}
void audio_uart_lv_area_expand_450b98(void *a,int32_t x,int32_t y){}
void audio_uart_ambiq_area_move_450bb2(void *a,int32_t x,int32_t y){}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
'''
LOWER=[("task",0x4843ee,"audio_uart_lv_render_task_alloc_4843ee"),
       ("malloc",0x44f718,"audio_uart_lv_malloc"),
       ("queue",0x484476,"audio_uart_lv_render_task_queue_484476"),
       ("fill_init",0x451c3a,"audio_uart_lv_draw_descriptor_init_451c3a"),
       ("image_init",0x488918,"audio_uart_ambiq_image_options_init_488918"),
       ("text_init",0x489f5e,"audio_uart_lv_image_descriptor_init_489f5e"),
       ("source_type",0x488cb8,"audio_uart_lv_image_source_type_488cb8"),
       ("header",0x488f6a,"audio_uart_lv_image_header_488f6a"),
       ("text_size",0x489546,"audio_uart_page_event_calculate_489546"),
       ("transform",0x451082,"audio_uart_lv_area_transform_451082"),
       ("expand",0x450b98,"audio_uart_lv_area_expand_450b98"),
       ("move",0x450bb2,"audio_uart_ambiq_area_move_450bb2"),
       ("log",0x44d25c,"audio_uart_lvgl_log")]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(p,n):p[:4]=(n&0xffffffff).to_bytes(4,"little")
def get32(p):return int.from_bytes(p[:4],"little")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_draw_task_render_451c6e",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def make_options(name):
            o=bytearray(0x80)
            o[0:0x1c]=bytes(range(0x20,0x3c))
            put32(memoryview(o)[0x1c:],0x64)
            if name in ("arc","all"):
                put32(memoryview(o)[0x5c:],2);put32(memoryview(o)[0x68:],3)
                put32(memoryview(o)[0x60:],2);put32(memoryview(o)[0x64:],-1)
                o[0x6c]=255
            if name in ("fill","fill_adjusted","all"):
                o[0x20]=255;o[0x2e]=2;o[0x2f]=1
                o[0x27]=255;o[0x2c]=255
            if name=="fill_adjusted":
                put32(memoryview(o)[0x44:],2);o[0x48]=255;o[0x49]=0x1f
            if name.startswith("image") or name=="all":
                put32(memoryview(o)[0x30:],0x20012000)
                put32(memoryview(o)[0x34:],0x20012100)
                o[0x3b]=255
                o[0x38:0x3b]=b"\x11\x22\x33"
                o[0x3c]=0x44
                o[0x3d]=1 if name=="image_unclipped" else 0
            if name in ("border","all"):
                put32(memoryview(o)[0x44:],5);o[0x48]=255;o[0x49]=0x0f
                o[0x3e:0x41]=b"\x31\x42\x53"
            if name in ("shadow","all"):
                put32(memoryview(o)[0x50:],5);put32(memoryview(o)[0x54:],2)
                o[0x58]=255;o[0x4a:0x4d]=b"\x63\x74\x85"
            return bytes(o)
        def run(compiled,name,kind,header_valid,fail_malloc=False):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            layer,area,source,options=(0x20010000,0x20011000,0x20012000,0x20013000)
            box=b"".join(x.to_bytes(4,"little",signed=True) for x in (10,20,40,50))
            l=bytearray(0x60);l[0x18:0x28]=box
            c.mem_write(layer,bytes(l));c.mem_write(area,box)
            c.mem_write(source,b"example\0"+bytes(0x80))
            c.mem_write(source+0x100,bytes(0x40))
            c.mem_write(options,make_options(name))
            for i in range(6):
                c.mem_write(0x20018000+i*0x100,bytes(0x80))
                c.mem_write(0x20020000+i*0x100,bytes([0xa5])*0x80)
            cuts={(syms[symbol]&~1) if compiled else address:label
                  for label,address,symbol in LOWER}
            trace=[];task_count=0;desc_count=0
            def hook(cpu,address,size,unused):
                nonlocal task_count,desc_count
                op=cuts.get(address)
                if op is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in
                             (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                result=0
                if op=="task":
                    slot=0x20018000+task_count*0x100;task_count+=1
                    raw=bytes(cpu.mem_read(r1,16))
                    cpu.mem_write(slot+8,raw);cpu.mem_write(slot+0x18,raw)
                    cpu.mem_write(slot+0x38,box)
                    cpu.mem_write(slot+0x48,layer.to_bytes(4,"little"))
                    cpu.mem_write(slot+0x50,(1).to_bytes(4,"little"))
                    trace.append((op,r0,raw));result=slot
                elif op=="malloc":
                    trace.append((op,r0))
                    if fail_malloc:result=0
                    else:
                        slot=0x20020000+desc_count*0x100;desc_count+=1
                        result=slot
                elif op=="queue":
                    task=bytes(cpu.mem_read(r1,0x60))
                    d=get32(task[0x54:0x58]);desc=bytes(cpu.mem_read(d,0x80))
                    trace.append((op,r0,r1,task,desc))
                elif op in ("fill_init","image_init","text_init"):
                    n={"fill_init":0x30,"image_init":0x6c,"text_init":100}[op]
                    cpu.mem_write(r0,bytes(n));trace.append((op,r0))
                elif op=="source_type":trace.append((op,r0));result=kind
                elif op=="header":
                    cpu.mem_write(r1,(0x11223344).to_bytes(4,"little")+
                                  ((4<<16)|8).to_bytes(4,"little")+
                                  (0x55667788).to_bytes(4,"little"))
                    trace.append((op,r0));result=header_valid
                elif op=="text_size":
                    cpu.mem_write(r0,(8).to_bytes(4,"little")+(4).to_bytes(4,"little"))
                    trace.append((op,r1,r2,r3));result=0
                elif op=="transform":
                    trace.append((op,r2,bytes(cpu.mem_read(r1,16))))
                elif op in ("expand","move"):
                    data=bytearray(cpu.mem_read(r0,16))
                    for i in range(4):
                        value=get32(data[i*4:i*4+4])
                        delta=(r1 if i%2==0 else r2)
                        if op=="expand":value=(value-delta) if i<2 else (value+delta)
                        else:value+=delta
                        put32(memoryview(data)[i*4:],value)
                    cpu.mem_write(r0,bytes(data))
                    trace.append((op,r1,r2))
                elif op=="log":
                    def string(ptr):return bytes(cpu.mem_read(ptr,160)).split(b"\0",1)[0]
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    words=[get32(cpu.mem_read(sp+i*4,4)) for i in range(3)]
                    trace.append((op,r0,string(r1),r2,string(r3),
                                  *(string(p) for p in words)))
                    cpu.emu_stop();return
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,layer)
            c.reg_write(A.UC_ARM_REG_R1,options)
            c.reg_write(A.UC_ARM_REG_R2,area)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_draw_task_render_451c6e"] if compiled else 0x451c6e
            c.emu_start(entry|1,0x600000,count=100000)
            tasks=[bytes(c.mem_read(0x20018000+i*0x100,0x80)) for i in range(task_count)]
            descs=[bytes(c.mem_read(0x20020000+i*0x100,0x80)) for i in range(desc_count)]
            return trace,tasks,descs,bytes(c.mem_read(options,0x80))
        cases=[("none",0,1),("arc",0,1),("fill",0,1),("fill_adjusted",0,1),
               ("image_clipped",0,1),("image_unclipped",1,1),
               ("image_clipped",0,0),("image_text",2,1),("image_skip",3,1),
               ("border",0,1),("shadow",0,1),("all",2,1)]
        cases += [(name,kind,1,True) for name,kind in
                  (("arc",0),("fill",0),("image_clipped",0),
                   ("image_text",2),("border",0),("shadow",0))]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                first=next(((i,a,b) for i,(a,b) in enumerate(zip(native[0],source[0]))
                            if a!=b),None)
                raise AssertionError((case,len(native[0]),len(source[0]),first,
                    [a==b for a,b in zip(native,source)]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_RENDER_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,
             "native_span":"0x451c6e..0x4522a7","cases":len(cases),
             "controlled_provider_count":len(LOWER),
             "limits":["All five task branches compared with controlled allocation and lower providers.",
                       "Allocation failure, live clipping, image decoding and display dispatch remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
