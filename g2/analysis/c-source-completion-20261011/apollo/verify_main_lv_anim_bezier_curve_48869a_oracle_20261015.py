#!/usr/bin/env python3
"""Compare fixed-point Bezier solver and polynomial with Apollo native code."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_bezier_curve_48869a.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-bezier-curve-48869a"
SHIM='''#include <stdint.h>
int64_t audio_uart_lv_div64_47cc1c(int64_t a,int64_t b){return 0;}
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def signed(value,bits):return value-(1<<bits) if value&(1<<(bits-1)) else value

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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_bezier_curve_48869a",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,args):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            trace=[]
            cut=(syms["audio_uart_lv_div64_47cc1c"]&~1) if compiled else 0x47cc1c
            def hook(cpu,address,size,unused):
                if address!=cut:return
                words=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                 A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                numerator=signed(words[0]|(words[1]<<32),64)
                denominator=signed(words[2]|(words[3]<<32),64)
                trace.append((numerator,denominator))
                if denominator==0:raise ZeroDivisionError(trace)
                q=(abs(numerator)//abs(denominator))*(-1 if (numerator<0) != (denominator<0) else 1)
                q&=(1<<64)-1
                cpu.reg_write(A.UC_ARM_REG_R0,q&0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_R1,q>>32)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,
                                  A.UC_ARM_REG_R3),args[:4]):u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            if len(args)>4:u.mem_write(0x203ff000,args[4].to_bytes(4,"little"))
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            name="audio_uart_lv_anim_polynomial_488686" if kind=="polynomial" else \
                "audio_uart_lv_anim_bezier_curve_48869a"
            origin=syms[name] if compiled else (0x488686 if kind=="polynomial" else 0x48869a)
            u.emu_start(origin|1,0x600000,count=500000)
            return trace,u.reg_read(A.UC_ARM_REG_R0)

        vals=(0,1,0x200,0x400,0xffffffff,0x80000000)
        polynomial=[("polynomial",args) for args in itertools.product(vals,repeat=4)]
        curve=[("curve",(t,x1,y1,x2,y2)) for t,x1,y1,x2,y2 in itertools.product(
            (0,1,0x80,0x200,0x400,0x500,0xffffffff),
            (0,0x155,0x300),(0,0x200),(0x251,0x400),(0x400,0x100))]
        cases=polynomial+curve
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_BEZIER_CURVE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x488686..0x488699","0x48869a..0x4887bb"],
             "cases":len(cases),"limits":["Signed 64-bit division controlled; full scheduler open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
