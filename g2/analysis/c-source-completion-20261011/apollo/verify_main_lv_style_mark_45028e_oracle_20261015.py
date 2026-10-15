#!/usr/bin/env python3
"""Compare Apollo active style marker against controlled LV list graphs."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_lv_style_mark_45028e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-style-mark-45028e"
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    if int.from_bytes(blob[0x4502b4-0x438000:0x4502b8-0x438000],"little")!=0x2006f548:raise RuntimeError("LV root literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text("unsigned char audio_uart_display_lv_state[0x100];\n")
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_style_mark_45028e",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            count,style,pattern=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x800000)
            nodes=[0x20011000+i*0x100 for i in range(3)]
            for i,a in enumerate(nodes):
                c.mem_write(a,bytes([0x44])*0x30)
                put(c,a,style if pattern[i]==1 else 0x12345678)
                put(c,a+4,style if pattern[i]==2 else 0x87654321)
                put(c,a+0x14,nodes[i+1] if i+1<count else 0)
                c.mem_write(a+0x18,bytes([0x02+i]))
            root=syms['audio_uart_display_lv_state'] if compiled else 0x2006f548
            put(c,root+0x6c,nodes[0] if count else 0)
            c.reg_write(A.UC_ARM_REG_R0,style)
            c.reg_write(A.UC_ARM_REG_SP,0x207ff000);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((syms['audio_uart_lv_style_mark_45028e'] if compiled else 0x45028e)|1,0x600000,count=1000)
            return c.reg_read(A.UC_ARM_REG_R0),[bytes(c.mem_read(a,0x20)) for a in nodes]
        cases=list(itertools.product((0,1,3),(0,0x20018000),( (0,0,0),(1,0,0),(2,1,0),(0,2,1),(1,1,2),(2,2,2) )))
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_STYLE_MARK_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_span":"0x45028e..0x4502b1","cases":len(cases),"limits":["Controlled list graphs only; concurrent LV state and final RAM root placement remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt['status'],len(cases))
if __name__=='__main__':main()
