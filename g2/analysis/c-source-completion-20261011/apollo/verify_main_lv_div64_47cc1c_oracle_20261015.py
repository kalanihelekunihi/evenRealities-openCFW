#!/usr/bin/env python3
"""Compare signed 64-bit quotient from native helper with C provider."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_div64_47cc1c.c"
OUT=G2/"build/c-firmware/20261015/main-lv-div64-47cc1c"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"test.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_div64_47cc1c",
                        str(SOURCE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,numerator,denominator):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            n=numerator&((1<<64)-1)
            d=denominator&((1<<64)-1)
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,
                                  A.UC_ARM_REG_R3),(n&0xffffffff,n>>32,d&0xffffffff,d>>32)):
                u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms["audio_uart_lv_div64_47cc1c"] if compiled else 0x47cc1c
            u.emu_start(origin|1,0x600000,count=1000000)
            return u.reg_read(A.UC_ARM_REG_R0)|(u.reg_read(A.UC_ARM_REG_R1)<<32)
        values=(0,1,-1,2,-2,1024,-1024,2**31-1,-2**31,2**32-1,
                2**40,-2**40,2**63-1,-2**63)
        divisors=tuple(x for x in values if x!=0)
        cases=list(itertools.product(values,divisors))
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,hex(native),hex(source)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_DIV64_QUOTIENT_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_entry":"0x47cc1c",
             "cases":len(cases),"limits":["Quotient registers compared; remainder ABI and zero-divisor path remain unproven."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
