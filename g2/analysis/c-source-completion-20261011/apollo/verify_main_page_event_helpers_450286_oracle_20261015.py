#!/usr/bin/env python3
"""Native/C comparison of page event code, extent and pending text helpers."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_event_helpers_450286.c"
OUT=G2/"build/c-firmware/20261015/main-page-event-helpers-450286"
SHIM='''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t l,const char*f,uint32_t n,const char*fn,const char*m,...)
{(void)l;(void)f;(void)n;(void)fn;(void)m;}
'''
FUNCS={"code":(0x450286,"audio_uart_page_event_code_450286"),
       "extent":(0x4519fa,"audio_uart_page_event_extent_4519fa"),
       "prepare":(0x49aacc,"audio_uart_page_event_prepare_49aacc")}
def put32(cpu,a,v):cpu.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))

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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_event_code_450286",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            op,code,value,offset,text=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            event,page,extent,buffer=0x20010000,0x20011000,0x20012000,0x20013000
            cpu.mem_write(event,bytes([0xa5])*0x30)
            cpu.mem_write(page,bytes([0x47])*0x80)
            cpu.mem_write(extent,bytes([0x32])*0x20)
            cpu.mem_write(buffer,bytes([0x72])*0x80)
            put32(cpu,event+8,code);put32(cpu,event+0x10,extent)
            put32(cpu,extent,15)
            put32(cpu,page+0x2c,buffer);put32(cpu,page+0x34,offset)
            cpu.mem_write(page+0x30,text)
            log_target=syms["audio_uart_lvgl_log"] if compiled else 0x44d25c
            trace=[]
            def hook(cpu,address,size,_):
                if address!=(log_target&~1):return
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                args=tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                       A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                extra=int.from_bytes(cpu.mem_read(sp,4),"little")
                trace.append((*args,extra))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE,hook)
            native,sym=FUNCS[op]
            cpu.reg_write(A.UC_ARM_REG_R0,page if op=="prepare" else event)
            cpu.reg_write(A.UC_ARM_REG_R1,value)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            cpu.emu_start((syms[sym] if compiled else native)|1,0x600000,count=100000)
            result=cpu.reg_read(A.UC_ARM_REG_R0) if op=="code" else None
            return (trace,result,bytes(cpu.mem_read(page,0x80)),
                    bytes(cpu.mem_read(extent,0x20)),bytes(cpu.mem_read(buffer,0x80)))
        cases=[]
        for code in (0,0x1b,0x801b,0xffffffff):
            for value in (0,9,17,0xffffffff):
                cases.append(("code",code,value,0xffffffff,b"ABCD"))
                cases.append(("extent",code,value,0xffffffff,b"ABCD"))
        for offset,text in itertools.product((0xffffffff,0,5),
                                             (b"\x00BCD",b"A\x00CD",b"AB\x00D",b"ABC\x00",b"ABCD")):
            cases.append(("prepare",0,0,offset,text))
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:
                raise AssertionError((case,native[:2],source[:2],
                     [(i,a,b) for i,(a,b) in enumerate(zip(native[2],source[2])) if a!=b][:8],
                     native[3][:8],source[3][:8],native[4][:12],source[4][:12]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_HELPERS_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"cases":len(cases),
             "native_spans":["0x450286..0x45028d","0x4519fa..0x451a29","0x49aacc..0x49ab05"],
             "limits":["Logger callback controlled; source data placement and live event mutation remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
