#!/usr/bin/env python3
"""Compare Apollo LV state getter and scrolling-chain walk with stock."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_base_state_helpers.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-state-helpers"
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_obj_state_43e156",str(SRC),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            kind,state,chain=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x400000)
            obj,n1,n2,n3=0x20011000,0x20012000,0x20013000,0x20014000
            c.mem_write(obj,bytes([0xa5])*0x80)
            c.mem_write(obj+0x28,(state&0xffff).to_bytes(2,"little"))
            put(c,obj,n1 if chain else 0)
            for i,node in enumerate((n1,n2,n3)):
                c.mem_write(node,bytes([0x55])*0x40)
                put(c,node,(n2,n3,0)[i])
                c.mem_write(node+0x20,bytes([(chain>>(i*2))&3]))
            c.reg_write(A.UC_ARM_REG_R0,obj);c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            name='audio_uart_lv_obj_state_43e156' if kind=='state' else 'audio_uart_lv_obj_is_scrolling_44d19a'
            c.emu_start((syms[name] if compiled else (0x43e156 if kind=='state' else 0x44d19a))|1,0x600000,count=1000)
            return c.reg_read(A.UC_ARM_REG_R0),bytes(c.mem_read(obj,0x40))
        cases=[('state',v,0) for v in (0,1,2,3,0x1234,0xffff)]
        cases += [('scroll',0,chain) for chain in range(64)]
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_STATE_HELPERS_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_spans":["0x43e156..0x43e183","0x44d19a..0x44d1cb"],"cases":len(cases),"limits":["Valid object pointers and controlled acyclic chains only; concurrent state mutation remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt['status'],len(cases))
if __name__=='__main__':main()
