#!/usr/bin/env python3
"""Compare Apollo render-task cleanup with controlled stock providers."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_render_task_free_4848e8.c"
OUT=G2/"build/c-firmware/20261015/main-lv-render-task-free-4848e8"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_area_height_4515a4(const void *p){return 0;}
void audio_uart_font_bitmap_release(void *p){}
void audio_uart_lv_heap_free(void *p){}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,... ){}
'''
LOWER=[("height",0x4515a4,"audio_uart_lv_area_height_4515a4"),
       ("release",0x48b216,"audio_uart_font_bitmap_release"),
       ("free",0x44f758,"audio_uart_lv_heap_free"),
       ("log",0x44d25c,"audio_uart_lvgl_log")]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_render_task_free_4848e8",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,kind,buffer_on,display_on,low_account,callback_on):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            display,task,desc,cell,draw,image_data,node,callback=(
                0x20010000,0x20011000,0x20012000,0x20013000,
                0x20014000,0x20015000,0x20016000,0x20017000)
            t=bytearray(0x60);t[4]=kind;t[0x54:0x58]=desc.to_bytes(4,"little")
            c.mem_write(task,bytes(t))
            d=bytearray(0x60)
            d[0x1c:0x20]=(cell if kind==7 else image_data).to_bytes(4,"little")
            d[0x54]=1 if kind==5 and buffer_on else 0
            c.mem_write(desc,bytes(d))
            x=bytearray(0x60);x[0:4]=(draw if buffer_on else 0).to_bytes(4,"little")
            x[0x4c:0x50]=(0x20018000).to_bytes(4,"little")
            c.mem_write(cell,bytes(x))
            b=bytearray(0x20);b[8:12]=(10).to_bytes(4,"little")
            c.mem_write(draw,bytes(b));c.mem_write(image_data,bytes(0x20))
            n=bytearray(0x60);n[0x4c:0x50]=cell.to_bytes(4,"little")
            c.mem_write(node,bytes(n));c.mem_write(0x20018000,bytes(0x60))
            dis=bytearray(0x2c0)
            dis[0x2ac:0x2b0]=node.to_bytes(4,"little")
            dis[0x2b4:0x2b8]=((callback|1) if callback_on else 0).to_bytes(4,"little")
            c.mem_write(display,bytes(dis));c.mem_write(callback,b"\x70\x47")
            c.mem_write(0x2006f68c,(2 if low_account else 100).to_bytes(4,"little"))
            cuts={(syms[name]&~1) if compiled else address:label
                  for label,address,name in LOWER}
            trace=[]
            def hook(cpu,address,size,unused):
                op="callback" if address==callback else cuts.get(address)
                if op is None:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in
                             (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                if op=="height":trace.append((op,r0));result=3
                elif op=="log":
                    fifth=int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little")
                    trace.append((op,r0,r1,r2,r3,fifth));result=0
                elif op=="callback":trace.append((op,r0,r1));result=0
                else:trace.append((op,r0));result=0
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,task)
            c.reg_write(A.UC_ARM_REG_R1,display if display_on else 0)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_render_task_free_4848e8"] if compiled else 0x4848e8
            c.emu_start(entry|1,0x600000,count=20000)
            return (trace,bytes(c.mem_read(task,0x60)),bytes(c.mem_read(desc,0x60)),
                    bytes(c.mem_read(cell,0x60)),bytes(c.mem_read(display,0x2c0)),
                    bytes(c.mem_read(node,0x60)),bytes(c.mem_read(0x2006f68c,4)))
        suite=[]
        for kind in (0,5,7):
            for buffer_on in (0,1):
                for display_on in (0,1):
                    for low_account in (0,1):
                        for callback_on in (0,1):
                            suite.append((kind,buffer_on,display_on,low_account,callback_on))
        for case in suite:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[0],source[0],
                                      [a==b for a,b in zip(native[1:],source[1:])]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_FREE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,
             "native_spans":["0x4848e8..0x4849a3","0x489fc8..0x489fd5"],
             "cases":len(suite),"controlled_lower_providers":len(LOWER),
             "limits":["Height, buffer release, heap free, logger and display callback are controlled.",
                       "Generic, image and draw-buffer task cleanup are compared; allocator internals remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(suite),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
