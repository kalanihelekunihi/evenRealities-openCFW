#!/usr/bin/env python3
"""Compare native animation descriptor defaults with compiled C."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_init_4503d6.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-init-4503d6"
SHIM='''#include <stdint.h>
int32_t audio_uart_lv_anim_default_path_450634(void *p){return 0;}
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_init_4503d6",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,seed,offset):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            addr=0x20010000+offset
            u.mem_write(addr,bytes(((seed+index*17)&0xff for index in range(96))))
            if not compiled:
                def zero(cpu,address,size,unused):
                    if address!=0x450398:return
                    pointer=cpu.reg_read(A.UC_ARM_REG_R0)
                    length=cpu.reg_read(A.UC_ARM_REG_R1)
                    if length!=96:raise AssertionError(length)
                    cpu.mem_write(pointer,bytes(length))
                    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,zero)
            u.reg_write(A.UC_ARM_REG_R0,addr)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms["audio_uart_lv_anim_init_4503d6"] if compiled else 0x4503d6
            u.emu_start(origin|1,0x600000,count=100000)
            data=bytearray(u.mem_read(addr,96))
            pointer=int.from_bytes(data[0x20:0x24],"little")
            expected=(syms["audio_uart_lv_anim_default_path_450634"]|1) if compiled else 0x450635
            if pointer!=expected:raise AssertionError((compiled,hex(pointer),hex(expected)))
            data[0x20:0x24]=bytes(4)
            return bytes(data)
        cases=[(seed,offset) for seed in (0,1,0x55,0xff) for offset in (0,4,16,32)]
        for case in cases:
            if run(False,*case)!=run(True,*case):raise AssertionError(case)
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_INIT_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,"native_span":"0x4503d6..0x450407",
             "cases":len(cases),"limits":["Zero helper controlled; default path pointer identity compared.",
                                     "Default path and scheduler runtime remain unresolved."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
