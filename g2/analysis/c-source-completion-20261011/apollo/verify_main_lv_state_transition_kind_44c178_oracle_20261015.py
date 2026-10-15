#!/usr/bin/env python3
"""Compare Apollo state refresh classification and property lookup order."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_state_transition_kind_44c178.c"
OUT=G2/"build/c-firmware/20261015/main-lv-state-transition-kind-44c178"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
uint32_t audio_uart_lv_style_reference_43dce0(void *s,uint32_t p,void *r){return 0;}
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(p,n):p[:4]=(n&0xffffffff).to_bytes(4,"little")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_state_transition_kind_44c178",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,count,previous,next_state,disabled,present):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            obj,records=0x20010000,0x20011000
            styles=(0x20012000,0x20012100)
            o=bytearray(0x50);put32(memoryview(o)[0x0c:],records)
            o[0x2a:0x2c]=(count<<4).to_bytes(2,"little")
            c.mem_write(obj,bytes(o))
            r=bytearray(0x20)
            for i in range(2):
                put32(memoryview(r)[i*8:],styles[i])
                put32(memoryview(r)[i*8+4:],(1<<i)|(0x02000000 if disabled&(1<<i) else 0))
            c.mem_write(records,bytes(r))
            cut=(syms["audio_uart_lv_style_reference_43dce0"]&~1) if compiled else 0x482946
            trace=[]
            def hook(cpu,address,size,unused):
                if address!=cut:return
                style=cpu.reg_read(A.UC_ARM_REG_R0)
                prop=cpu.reg_read(A.UC_ARM_REG_R1)
                result_ptr=cpu.reg_read(A.UC_ARM_REG_R2)
                index=styles.index(style)
                hit=prop in present[index]
                trace.append((index,prop))
                if hit:cpu.mem_write(result_ptr,(0x1234).to_bytes(4,"little"))
                cpu.reg_write(A.UC_ARM_REG_R0,1 if hit else 0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,obj)
            c.reg_write(A.UC_ARM_REG_R1,previous)
            c.reg_write(A.UC_ARM_REG_R2,next_state)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_state_transition_kind_44c178"] if compiled else 0x44c178
            c.emu_start(entry|1,0x600000,count=100000)
            return c.reg_read(A.UC_ARM_REG_R0),trace,bytes(c.mem_read(obj,0x50))
        cases=[
            (0,0,1,0,((),())),
            (1,0,0,0,((),())),
            (1,0,1,1,((),())),
            (1,0,1,0,((),())),
            (1,0,1,0,((0x10,),())),
            (1,0,1,0,((0x30,),())),
            (1,0,1,0,((0x6a,),())),
            (1,0,1,0,((0x48,),())),
            (2,0,3,0,((0x6a,),())),
            (2,0,3,0,((0x6a,),(0x30,))),
            (2,0,3,0,((),(0x48,))),
            (2,1,3,0,((0x10,),(0x6a,))),
            (2,3,0,0,((0x10,),())),
            (2,0,3,2,((0x10,),(0x48,))),
        ]
        for case in cases:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                first=next(((i,a,b) for i,(a,b) in enumerate(zip(native[1],source[1])) if a!=b),None)
                raise AssertionError((case,native[0],source[0],len(native[1]),len(source[1]),first))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_STATE_TRANSITION_KIND_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,"native_span":"0x44c178..0x44c447",
             "cases":len(cases),
             "limits":["Geometry and layout property priority, disabled records and active-state changes compared.",
                       "Style property lookup responses are controlled; live style storage remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
