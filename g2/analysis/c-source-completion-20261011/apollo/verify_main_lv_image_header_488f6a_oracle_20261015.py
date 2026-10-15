#!/usr/bin/env python3
"""Compare Apollo LV image-header wrapper with controlled decoder providers."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_image_header_488f6a.c"
OUT=G2/"build/c-firmware/20261015/main-lv-image-header-488f6a"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
void audio_uart_lv_image_memzero_488f40(void *p,uint32_t n){}
uint32_t audio_uart_lv_image_source_type_488cb8(const void *p){return 0;}
uint32_t audio_uart_lv_decoder_find_48925a(void *p,void *h){return 0;}
'''
LOWER=[("zero",0x488f40,"audio_uart_lv_image_memzero_488f40"),
       ("type",0x488cb8,"audio_uart_lv_image_source_type_488cb8"),
       ("find",0x48925a,"audio_uart_lv_decoder_find_48925a")]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_image_header_488f6a",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,source_type,found,fill):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            source,header=0x20010000,0x20011000
            c.mem_write(source,bytes(range(32)))
            c.mem_write(header,bytes([fill])*0x20)
            cuts={(syms[name]&~1) if compiled else address:label
                  for label,address,name in LOWER}
            trace=[]
            def hook(cpu,address,size,unused):
                op=cuts.get(address)
                if op is None:return
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                if op=="zero":
                    trace.append((op,r1));cpu.mem_write(r0,bytes(r1));result=0
                elif op=="type":trace.append((op,r0));result=source_type
                else:
                    state=bytes(cpu.mem_read(r0,0x4c))
                    trace.append((op,r1,state))
                    if found:cpu.mem_write(r1,bytes(range(0xb0,0xbc)))
                    result=found
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,source)
            c.reg_write(A.UC_ARM_REG_R1,header)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_image_header_488f6a"] if compiled else 0x488f6a
            c.emu_start(entry|1,0x600000,count=20000)
            return c.reg_read(A.UC_ARM_REG_R0),trace,bytes(c.mem_read(header,0x20))
        suite=[(kind,found,fill) for kind in (0,1,2,3,0xff)
               for found in (0,1) for fill in (0,0xa5)]
        for case in suite:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[:2],source[:2],native[2]==source[2]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_IMAGE_HEADER_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,
             "native_span":"0x488f6a..0x488f9b","cases":len(suite),
             "controlled_lower_providers":len(LOWER),
             "limits":["Decoder initialization, type and header providers are controlled; live decoder content is open.",
                       "Full 0x4c-byte request state and header output are compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(suite),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
