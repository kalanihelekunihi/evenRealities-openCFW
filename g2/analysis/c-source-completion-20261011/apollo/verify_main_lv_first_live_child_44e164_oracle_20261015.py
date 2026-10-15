#!/usr/bin/env python3
"""Compare LVGL first non-deleting child selection with official Apollo."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_first_live_child_44e164.c"
OUT=G2/"build/c-firmware/20261015/main-lv-first-live-child-44e164"
SHIM='''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,...){}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_first_live_child_44e164",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,present,has_layer,count,mask):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            obj,layer,array=0x20010000,0x20011000,0x20012000
            children=[0x20013000+i*0x100 for i in range(3)]
            o=bytearray(64);o[8:12]=(layer if has_layer else 0).to_bytes(4,"little")
            l=bytearray(64);l[:4]=array.to_bytes(4,"little")
            l[0x30:0x32]=count.to_bytes(2,"little")
            u.mem_write(obj,bytes(o));u.mem_write(layer,bytes(l))
            u.mem_write(array,b''.join(x.to_bytes(4,"little") for x in children)+b"\0"*52)
            for i,child in enumerate(children):
                data=bytearray(64)
                data[0x2a:0x2c]=((0x1000 if mask & (1<<i) else 0) | 0xa5).to_bytes(2,"little")
                u.mem_write(child,bytes(data))
            logger=(syms["audio_uart_lvgl_log"]&~1) if compiled else 0x44d25c
            trace=[]

            def read_string(ptr):return bytes(u.mem_read(ptr,160)).split(b"\0",1)[0].decode("utf8","replace")

            def hook(cpu,address,size,unused):
                if address!=logger:return
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                args=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                args += [int.from_bytes(cpu.mem_read(sp+i*4,4),"little") for i in range(3)]
                trace.append((args[0],read_string(args[1]),args[2],
                              *[read_string(p) for p in args[3:]]))
                cpu.emu_stop()

            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,obj if present else 0)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_first_live_child_44e164"] if compiled else 0x44e164
            u.emu_start(entry|1,0x600000,count=100000)
            return (None if not present else u.reg_read(A.UC_ARM_REG_R0),trace)

        cases=list(itertools.product((0,1),(0,1),(0,1,2,3),range(8)))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_FIRST_LIVE_CHILD_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x44e164..0x44e1c7",
             "cases":len(cases),"limits":["Child-array scan and null-object logger entry are compared.",
             "Logger internals and fatal loop are not executed; child storage ownership is not proved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))


if __name__=="__main__":main()
