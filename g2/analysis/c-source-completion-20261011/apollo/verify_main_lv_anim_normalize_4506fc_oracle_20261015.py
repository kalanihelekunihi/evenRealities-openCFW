#!/usr/bin/env python3
"""Compare native LVGL packed speed conversion and descriptor normalization."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_anim_normalize_4506fc.c"
OUT=G2/"build/c-firmware/20261015/main-lv-anim-normalize-4506fc"

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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_anim_normalize_450a3e",
                        str(SOURCE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]

        def run(compiled,kind,packed,start,end):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
            u.mem_map(0x100000,0x100000)
            for addr,data in segments:u.mem_write(addr,data)
            u.mem_map(0x20000000,0x400000)
            addr=0x20010000
            if kind=="normalize":
                u.mem_write(addr,bytes([0x5a])*96)
                for offset,value in ((0x24,start),(0x2c,end),(0x30,packed),
                                     (0x3c,packed^0x3ff),(0x38,packed^0x100000),
                                     (0x40,packed^0x400)):
                    u.mem_write(addr+offset,value.to_bytes(4,"little"))
                args=(addr,0,0)
                name="audio_uart_lv_anim_normalize_450a3e"
                native=0x450a3e
            else:
                args=(packed,start,end)
                name="audio_uart_lv_anim_speed_to_time_4506fc"
                native=0x4506fc
            for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),args):
                u.reg_write(reg,value)
            u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR,0x600001)
            origin=syms[name] if compiled else native
            u.emu_start(origin|1,0x600000,count=100000)
            return bytes(u.mem_read(addr,96)) if kind=="normalize" else u.reg_read(A.UC_ARM_REG_R0)

        packed_values=(0,1,500,0x7fffffff,0x80000000,0x80000400,
                       0x8405a015,0xc0000001,0xffffffff)
        endpoints=((0,100),(100,0),(0,0),(0x7fffffff,0x80000000),
                   (0xffffffff,0x400))
        cases=list(itertools.product(("helper","normalize"),packed_values,endpoints))
        for kind,packed,(start,end) in cases:
            case=(kind,packed,start,end)
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_ANIM_NORMALIZE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":digest,
             "native_spans":["0x4506fc..0x450757","0x450a3e..0x450a73"],
             "cases":len(cases),"limits":["Packed conversion and 96-byte descriptor state compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))

if __name__=="__main__":main()
