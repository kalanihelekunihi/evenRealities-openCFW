#!/usr/bin/env python3
"""Compare Apollo palette values and image descriptor defaults with stock Main."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_image_descriptor_init_489f5e.c"
OUT=G2/"build/c-firmware/20261015/main-lv-image-descriptor-init-489f5e"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM='''#include <stdint.h>
const unsigned char audio_uart_display_page_style[36]={0};
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,... ){}
'''

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    palette=blob[0x716330-0x438000:0x716330-0x438000+57]
    with tempfile.TemporaryDirectory() as directory:
        elf,shim=Path(directory)/"test.elf",Path(directory)/"shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_image_descriptor_init_489f5e",
                        str(SOURCE),str(shim),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,entry_kind,value):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            desc=0x20013000;c.mem_write(desc,bytes([value])*0x80)
            logs=[]
            cut=(syms["audio_uart_lvgl_log"]&~1) if compiled else 0x44d25c
            def read_string(ptr):return bytes(c.mem_read(ptr,160)).split(b"\0",1)[0]
            def hook(cpu,address,size,unused):
                if address!=cut:return
                r0,r1,r2,r3=(cpu.reg_read(r) for r in
                             (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                fmt=int.from_bytes(cpu.mem_read(sp,4),"little")
                index=int.from_bytes(cpu.mem_read(sp+4,4),"little")
                logs.append((r0,read_string(r1),r2,read_string(r3),read_string(fmt),index))
                cpu.reg_write(A.UC_ARM_REG_R0,0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,desc if entry_kind=="descriptor" else value)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=(syms["audio_uart_lv_image_descriptor_init_489f5e"] if compiled else 0x489f5e) \
                if entry_kind=="descriptor" else \
                (syms["audio_uart_page_488290"] if compiled else 0x488290)
            c.emu_start(entry|1,0x600000,count=20000)
            data=bytearray(c.mem_read(desc,0x80))
            if entry_kind=="descriptor":
                style=syms["audio_uart_display_page_style"] if compiled else 0x755610
                if int.from_bytes(data[0x20:0x24],"little")!=style:
                    raise AssertionError(("style",compiled,value,hex(style),data[0x20:0x24].hex()))
                data[0x20:0x24]=b"STYL"
                return logs,bytes(data)
            return logs,c.reg_read(A.UC_ARM_REG_R0)&0xffffff
        descriptor_cases=(0,0x55,0xa5,0xff)
        for fill in descriptor_cases:
            native,source=run(False,"descriptor",fill),run(True,"descriptor",fill)
            if native!=source:raise AssertionError(("descriptor",fill,native,source))
        palette_cases=tuple(range(19))+(19,255)
        for index in palette_cases:
            native,source=run(False,"palette",index),run(True,"palette",index)
            if native!=source:raise AssertionError(("palette",index,native,source))
        source_table=bytes().join(bytes((x,)) for x in palette)
        if len(source_table)!=57:raise RuntimeError("palette length changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DESCRIPTOR_INIT_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,
             "native_spans":["0x488290..0x4882d1","0x489f5e..0x489fc7"],
             "palette_table_native_address":"0x716330","palette_table_sha256":hashlib.sha256(palette).hexdigest(),
             "cases":len(descriptor_cases)+len(palette_cases),
             "limits":["Descriptor bytes and palette RGB triples are compared; stock palette return top byte is unwritten.",
                       "Source-owned style pointer is normalized to stock ROM address."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],receipt["cases"],sha(OUT/"oracle.json"))

if __name__=="__main__":main()
