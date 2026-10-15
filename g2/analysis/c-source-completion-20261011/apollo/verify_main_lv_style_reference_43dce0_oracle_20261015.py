#!/usr/bin/env python3
"""Compare Apollo packed and sparse style property references with stock Main."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_style_reference_43dce0.c"
OUT=G2/"build/c-firmware/20261015/main-lv-style-reference-43dce0"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put32(p,n):p[:4]=(n&0xffffffff).to_bytes(4,"little")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf=Path(directory)/"test.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_style_reference_43dce0",
                        str(SOURCE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,sparse,count,key,fill):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            style,data,result=0x20010000,0x20011000,0x20012000
            s=bytearray(0x10);put32(memoryview(s),data);s[8]=0xff if sparse else count
            c.mem_write(style,bytes(s))
            d=bytearray(0x80)
            keys=(0x42,0x68,0x77)
            values=(0x20013000,0x20014000,0x20015000)
            if sparse:
                for i in range(count):
                    d[i*8]=keys[i];put32(memoryview(d)[i*8+4:],values[i])
            else:
                for i in range(count):
                    put32(memoryview(d)[i*4:],values[i]);d[count*4+i]=keys[i]
            c.mem_write(data,bytes(d));c.mem_write(result,bytes([fill])*4)
            c.reg_write(A.UC_ARM_REG_R0,style)
            c.reg_write(A.UC_ARM_REG_R1,key)
            c.reg_write(A.UC_ARM_REG_R2,result)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_style_reference_43dce0"] if compiled else 0x43dce0
            c.emu_start(entry|1,0x600000,count=20000)
            return c.reg_read(A.UC_ARM_REG_R0),bytes(c.mem_read(result,4)),bytes(c.mem_read(data,0x80))
        suite=[(sparse,count,key,fill)
               for sparse in (0,1) for count in (0,1,2,3)
               for key in (0x42,0x68,0x77,0x99,0x168)
               for fill in (0,0xa5)]
        for case in suite:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_STYLE_REFERENCE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,"native_span":"0x43dce0..0x43dd47",
             "cases":len(suite),"formats":["packed","sparse"],
             "limits":["Packed and sparse lookups with present and missing keys are native-compared.",
                       "Malformed style pointers and unterminated sparse tables are not covered."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(suite),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
