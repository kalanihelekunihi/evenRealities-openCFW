#!/usr/bin/env python3
"""Compare Apollo glyph iterator against stock with real C/stock decoders."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_text_next_glyph_489b3c.c"
DEC=G2/"components/audio/uart_thread_source_candidate/display_page_text_decode_489c5e.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-next-glyph-489b3c"
def put(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get(c,a):return int.from_bytes(c.mem_read(a,4),"little")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_next_glyph_489b3c",
                        str(SRC),str(DEC),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,raw,offset):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x400000)
            t,g,n,o=0x20011000,0x20012000,0x20012004,0x20012008
            c.mem_write(t,b"X"*offset+raw+b"\x00"*8)
            for a,v in ((g,0xdeadbeef),(n,0xdeadbeef),(o,offset)):put(c,a,v)
            for reg,value in ((A.UC_ARM_REG_R0,t),(A.UC_ARM_REG_R1,g),
                              (A.UC_ARM_REG_R2,n),(A.UC_ARM_REG_R3,o),
                              (A.UC_ARM_REG_SP,0x203ff000),(A.UC_ARM_REG_LR,0x600001)):
                c.reg_write(reg,value)
            entry=syms["audio_uart_text_next_glyph_489b3c"] if compiled else 0x489b3c
            c.emu_start(entry|1,0x600000,count=10000)
            return get(c,g),get(c,n),get(c,o)
        patterns=(b"",b"A",b"AB",b"ABC",b"\xc2\xa2",b"\xc2\xa2B",
                  b"\xe2\x82\xac",b"\xe2\x82\xacA",b"\xf0\x9f\x98\x80",
                  b"\xf0\x9f\x98\x80B",b"\x80",b"\xc2A",b"\xe2\x82A")
        cases=list(itertools.product(patterns,(0,1,2)))
        for raw,offset in cases:
            stock,source=run(False,raw,offset),run(True,raw,offset)
            if stock!=source:raise AssertionError(((raw,offset),stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_NEXT_GLYPH_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "decoder_source_sha256":hashlib.sha256(DEC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x489b3c..0x489b73",
             "cases":len(cases),"limits":["Native/C glyph pair iteration uses real UTF-8 decoder bodies in both paths; full font rendering remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
