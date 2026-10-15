#!/usr/bin/env python3
"""Native/C page event text finalization with stock and C copy providers."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_event_finish_49ab06.c"
COPY=G2/"components/audio/uart_thread_source_candidate/display_settings_copy_text.c"
OUT=G2/"build/c-firmware/20261015/main-page-event-finish-49ab06"
SHIM='''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t l,const char*f,uint32_t n,const char*fn,const char*m,...)
{(void)l;(void)f;(void)n;(void)fn;(void)m;}
'''
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_event_finish_49ab06",
                        str(SOURCE),str(COPY),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            current,old,text=case
            cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
            cpu.mem_map(0x100000,0x100000)
            for addr,data in segments:cpu.mem_write(addr,data)
            cpu.mem_map(0x20000000,0x400000)
            page,buffer=0x20011000,0x20012000
            cpu.mem_write(page,bytes([0xa5])*0x80)
            cpu.mem_write(buffer,bytes([0x72])*0x80)
            put32(cpu,page+0x2c,buffer);put32(cpu,page+0x34,current)
            cpu.mem_write(buffer,text+bytes([0x55])*4)
            log_target=syms["audio_uart_lvgl_log"] if compiled else 0x44d25c
            trace=[]
            def hook(cpu,address,size,_):
                if address!=(log_target&~1):return
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                args=tuple(cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                extra=tuple(int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3))
                trace.append((*args,*extra));cpu.emu_stop()
            cpu.hook_add(UC_HOOK_CODE,hook)
            cpu.reg_write(A.UC_ARM_REG_R0,page)
            cpu.reg_write(A.UC_ARM_REG_R1,old)
            cpu.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_page_event_finish_49ab06"] if compiled else 0x49ab06
            cpu.emu_start(entry|1,0x600000,count=100000)
            return trace,bytes(cpu.mem_read(page,0x80)),bytes(cpu.mem_read(buffer,0x80))
        patterns=(b"\x00BCD",b"A\x00CD",b"AB\x00D",b"ABC\x00",b"ABCD")
        cases=[(0xffffffff,old,text) for old,text in itertools.product((-1,0,5),patterns)]
        cases.append((0,0,b"ABCD"))
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:
                raise AssertionError((case,stock[0],source[0],
                    [(i,a,b) for i,(a,b) in enumerate(zip(stock[1],source[1])) if a!=b][:8],
                    [(i,a,b) for i,(a,b) in enumerate(zip(stock[2],source[2])) if a!=b][:8]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_FINISH_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "copy_source_sha256":hashlib.sha256(COPY.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x49ab06..0x49ab75",
             "cases":len(cases),
             "limits":["Normal paths compare against stock copy provider and compiled C copy body.",
                       "Fatal path log arguments match; subsequent fault loop is not executed."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
