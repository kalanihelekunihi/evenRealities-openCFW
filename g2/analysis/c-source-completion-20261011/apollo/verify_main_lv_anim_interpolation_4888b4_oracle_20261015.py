#!/usr/bin/env python3
"""Compare native linear interpolation and Bezier wrapper with C."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_interpolation_4888b4.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-interpolation-4888b4"
SHIM='''#include <stdint.h>
int32_t audio_uart_lv_anim_bezier_curve_48869a(int32_t a,int32_t b,int32_t c,int32_t d,int32_t e){return 0;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_interpolate_4888b4",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,args,curve=0):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            stack=0x203ff000
            descriptor=0x20010000
            trace=[]
            if kind=="bezier":
                elapsed,duration,from_value,to_value,c1,c2,c3,c4=args
                for offset,value in ((0x24,from_value),(0x2c,to_value),
                                     (0x30,duration),(0x34,elapsed)):
                    u.mem_write(descriptor+offset,value.to_bytes(4,"little"))
                arguments=(descriptor,c1,c2,c3,c4)
                cut=(syms["audio_uart_lv_anim_bezier_curve_48869a"]&~1) if compiled else 0x48869a
                def hook(cpu,address,size,unused):
                    if address!=cut:return
                    regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                    A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                    fifth=int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little")
                    trace.append((*regs,fifth))
                    cpu.reg_write(A.UC_ARM_REG_R0,curve)
                    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook)
            else:arguments=args
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,
                                  A.UC_ARM_REG_R3),arguments[:4]):u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,stack)
            u.mem_write(stack,arguments[4].to_bytes(4,"little"))
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            name="audio_uart_lv_anim_bezier_450a04" if kind=="bezier" else \
                "audio_uart_lv_anim_interpolate_4888b4"
            origin=syms[name] if compiled else (0x450a04 if kind=="bezier" else 0x4888b4)
            u.emu_start(origin|1,0x600000,count=100000)
            return trace,u.reg_read(A.UC_ARM_REG_R0)

        linear=[(p,s,e,0,0x400) for (s,e),p in itertools.product(
            ((0,100),(100,0),(0,0),(0x80000000,0x7fffffff),
             (0x7fffffff,0x80000000),(0xfffffffe,1)),
            (0,1,25,50,99,100,101,0xffffffff,0x80000000,0x7fffffff))]
        linear += [(p,s,e,a,b) for (s,e),p,(a,b) in itertools.product(
            ((0,100),(100,0)),(25,50,75),
            ((0xffffffff,0x7fffffff),(0x80000000,1),(123,456)))]
        bezier=[(elapsed,duration,from_value,to_value,0,0,0x251,0x400)
                for elapsed,duration,from_value,to_value in itertools.product(
                    (0,250,500,0xffffffff),(0,500),
                    (0,0x80000000),(100,0xffffffff))]
        cases=[("linear",args,0) for args in linear] + [
            ("bezier",args,curve) for args in bezier for curve in (0,1,0x200,0x400,0xffffffff)]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_INTERPOLATION_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x4888b4..0x4888f5","0x450a04..0x450a3d"],
             "cases":len(cases),"limits":["Bezier curve lower call controlled; no scheduler runtime proof."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
