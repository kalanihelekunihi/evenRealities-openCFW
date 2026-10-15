#!/usr/bin/env python3
"""Compare LVGL position reset's two lower calls with Apollo."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_position_reset_44e9ba.c"
OUT=G2/"build/c-firmware/20261015/main-lv-position-reset-44e9ba"
SHIM='''#include <stdint.h>
void audio_uart_lv_scroll_to_x_44e9da(void *p,int32_t x,uint8_t a){}
void audio_uart_lv_scroll_to_y_44ea04(void *p,int32_t y,uint8_t a){}
'''


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_position_reset_44e9ba",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,x,y,animated):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj=0x20010000
            cuts={(syms[name]&~1) if compiled else addr:label for label,addr,name in
                  [("x",0x44e9da,"audio_uart_lv_scroll_to_x_44e9da"),
                   ("y",0x44ea04,"audio_uart_lv_scroll_to_y_44ea04")]}
            trace=[]

            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                trace.append((op,*[cpu.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2)]))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE,hook)
            for reg,value in ((A.UC_ARM_REG_R0,obj),(A.UC_ARM_REG_R1,x),
                              (A.UC_ARM_REG_R2,y),(A.UC_ARM_REG_R3,animated),
                              (A.UC_ARM_REG_SP,0x203ff000),(A.UC_ARM_REG_LR,0x600001)):
                u.reg_write(reg,value)
            entry=syms["audio_uart_lv_position_reset_44e9ba"] if compiled else 0x44e9ba
            u.emu_start(entry|1,0x600000,count=100000)
            return trace

        cases=list(itertools.product((0,1,0xffffffff,0x100),(0,1,0xffffffff,0x200),
                                     (0,1,0xff,0x100)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_POSITION_RESET_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44e9ba..0x44e9d9",
             "cases":len(cases),"limits":["Only two lower call targets and register arguments are compared.",
             "Horizontal and vertical movement bodies remain unresolved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
