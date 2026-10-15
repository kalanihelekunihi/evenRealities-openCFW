#!/usr/bin/env python3
"""Compare stock animation path wrappers with compiled C and controlled engines."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_paths_450634.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-paths-450634"
SHIM='''#include <stdint.h>
int32_t audio_uart_lv_anim_interpolate_4888b4(int32_t a,int32_t b,int32_t c,int32_t d,int32_t e){return 0;}
int32_t audio_uart_lv_anim_bezier_450a04(void *a,int32_t b,int32_t c,int32_t d,int32_t e){return 0;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_default_path_450634",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,start,end,elapsed,duration,progress):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            addr=0x20010000
            for offset,value in ((0x24,start),(0x2c,end),(0x30,duration),(0x34,elapsed)):
                u.mem_write(addr+offset,value.to_bytes(4,"little"))
            cuts={(syms["audio_uart_lv_anim_interpolate_4888b4"]&~1) if compiled else 0x4888b4:"interpolate",
                  (syms["audio_uart_lv_anim_bezier_450a04"]&~1) if compiled else 0x450a04:"bezier"}
            trace=[]
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                regs=[cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                fifth=int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little")
                trace.append((op,*regs,fifth))
                cpu.reg_write(A.UC_ARM_REG_R0,progress)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.reg_write(A.UC_ARM_REG_R0,addr)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            name="audio_uart_lv_anim_default_path_450634" if kind=="default" else "audio_uart_lv_anim_path_450672"
            origin=syms[name] if compiled else (0x450634 if kind=="default" else 0x450672)
            u.emu_start(origin|1,0x600000,count=100000)
            return trace,u.reg_read(A.UC_ARM_REG_R0)

        cases=[("default",a,b,t,d,p) for a,b,t,d,p in itertools.product(
            (0,1,0xffffffff,0x80000000),(0,1,0x7fffffff),
            (0,123),(0,500),(0,0x200,0x400,0xffffffff))]
        cases += [("bezier",0,0,0,0,p) for p in (0,1,0x400,0xffffffff)]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_PATHS_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x450634..0x450659","0x450672..0x450687"],
             "cases":len(cases),"limits":["Interpolation engines controlled; scheduler behavior remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
