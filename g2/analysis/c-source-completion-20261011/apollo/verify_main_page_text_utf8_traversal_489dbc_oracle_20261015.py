#!/usr/bin/env python3
"""Compare Apollo UTF-8 traversal callbacks with native code."""
import hashlib,itertools,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
DIR=G2/"components/audio/uart_thread_source_candidate"
SRC=DIR/"display_page_text_utf8_traversal_489dbc.c"
LENGTH=DIR/"display_page_text_utf8_length_489b74.c"
DECODE=DIR/"display_page_text_decode_489c5e.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-utf8-traversal-489dbc"
FUNCTIONS=(("previous",0x489dbc,"audio_uart_text_utf8_previous_489dbc"),
           ("bytes_for_count",0x489e14,"audio_uart_text_utf8_bytes_for_count_489e14"),
           ("count_to_bytes",0x489e4a,"audio_uart_text_utf8_count_to_bytes_489e4a"),
           ("count",0x489e6e,"audio_uart_text_utf8_count_489e6e"))
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
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_utf8_previous_489dbc",
                        str(SRC),str(LENGTH),str(DECODE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            kind,raw,n=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for addr,data in segments:c.mem_write(addr,data)
            c.mem_map(0x20000000,0x400000)
            text,offset=0x20011000,0x20012000
            c.mem_write(text,raw+b"\x00"*8)
            put(c,offset,n)
            c.reg_write(A.UC_ARM_REG_R0,text)
            c.reg_write(A.UC_ARM_REG_R1,offset if kind=="previous" else n if kind!="count" else 0xaabbccdd)
            c.reg_write(A.UC_ARM_REG_R2,0x12345678)
            c.reg_write(A.UC_ARM_REG_R3,0x87654321)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            target=next((native,name) for label,native,name in FUNCTIONS if label==kind)
            entry=syms[target[1]] if compiled else target[0]
            c.emu_start(entry|1,0x600000,count=100000)
            return c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1),get(c,offset)
        raws=(b"",b"A",b"ABC",b"\xc2\xa2",b"A\xc2\xa2B",
              b"\xe2\x82\xac",b"\xf0\x9f\x98\x80",b"A\xf0\x9f\x98\x80B",
              b"\x80",b"\xc2A")
        cases=[]
        for raw in raws:
            cases += [("previous",raw,n) for n in range(1,len(raw)+1)]
            cases += [("bytes_for_count",raw,n) for n in range(5)]
            cases += [("count_to_bytes",raw,n) for n in range(len(raw)+1)]
            cases += [("count",raw,0)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_TRAVERSAL_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "provider_source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (LENGTH,DECODE)},
             "official_payload_sha256":digest,
             "native_spans":["0x489dbc..0x489e13","0x489e14..0x489e49","0x489e4a..0x489e6d","0x489e6e..0x489e91"],
             "cases":len(cases),"limits":["Traversal is native compared over bounded buffers; zero-progress malformed input, null pointers, and final callback table placement remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
