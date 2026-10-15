#!/usr/bin/env python3
"""Compare Apollo two-level registry lookup with the official Main payload."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_registry_lookup_45fffe.c"
OUT=G2/"build/c-firmware/20261015/main-registry-lookup-45fffe"
def put32(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    if int.from_bytes(blob[0x46011c-0x438000:0x460120-0x438000],"little")!=0x200746cc or int.from_bytes(blob[0x460120-0x438000:0x460124-0x438000],"little")!=0x200746c8:raise RuntimeError("registry roots changed")
    with tempfile.TemporaryDirectory() as td:
        shim,elf=Path(td)/"shim.c",Path(td)/"oracle.elf"
        shim.write_text("const void *audio_uart_display_context_list_cell;\nconst void *audio_uart_display_context_active_cell;\n")
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_45fffe",str(SRC),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(["arm-none-eabi-nm",str(elf)],text=True).splitlines() if len(p:=line.split())==3}
        with elf.open("rb") as f:segs=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments() if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            index,first_present,first_table,first_value,same,second_table,second_value=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB);c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,data in segs:c.mem_write(a,data)
            c.mem_map(0x20000000,0x800000)
            first,root,second,tab1,tab2=0x20011000,0x20012000,0x20013000,0x20014000,0x20015000
            active_cell=syms["audio_uart_display_context_active_cell"] if compiled else 0x200746cc
            list_cell=syms["audio_uart_display_context_list_cell"] if compiled else 0x200746c8
            put32(c,active_cell,first if first_present else 0)
            put32(c,list_cell,root);put32(c,root,first if same else second)
            put32(c,first+4,tab1 if first_table else 0);put32(c,second+4,tab2 if second_table else 0)
            if index!=0xffff:
                put32(c,tab1+index*4,first_value);put32(c,tab2+index*4,second_value)
            c.reg_write(A.UC_ARM_REG_R0,0x12345678);c.reg_write(A.UC_ARM_REG_R1,index)
            c.reg_write(A.UC_ARM_REG_SP,0x207ff000);c.reg_write(A.UC_ARM_REG_LR,0x600001)
            c.emu_start((syms["audio_uart_page_45fffe"] if compiled else 0x45fffe)|1,0x600000,count=1000)
            return c.reg_read(A.UC_ARM_REG_R0)
        cases=list(itertools.product((0,1,3,0xffff),(0,1),(0,1),(0,0xaaaa5555),(0,1),(0,1),(0,0xbbbb6666)))
        for case in cases:
            native,source=run(False,case),run(True,case)
            if native!=source:raise AssertionError((case,hex(native),hex(source)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_REGISTRY_LOOKUP_ORACLE","source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"official_payload_sha256":digest,"native_span":"0x45fffe..0x46004f","registry_root_literals":["0x200746cc","0x200746c8"],"cases":len(cases),"limits":["Mapped RAM registry graphs are controlled; source-owned root cells require final placement and concurrent mutation is untested."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
