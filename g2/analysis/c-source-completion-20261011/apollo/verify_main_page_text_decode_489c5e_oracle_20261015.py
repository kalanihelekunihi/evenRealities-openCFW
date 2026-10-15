#!/usr/bin/env python3
"""Compare Apollo UTF-8 decoder C with the official native payload."""
import hashlib, itertools, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_decode_489c5e.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-decode-489c5e"
def put32(c,a,v):c.mem_write(a,(v&0xffffffff).to_bytes(4,"little"))
def get32(c,a):return int.from_bytes(c.mem_read(a,4),"little")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_decode_489c5e",
                        str(SOURCE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,case):
            raw,offset,missing_text,missing_offset=case
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for addr,data in segments:c.mem_write(addr,data)
            c.mem_map(0x20000000,0x400000)
            t,o=0x20011000,0x20012000
            c.mem_write(t,b"X"*offset+raw+b"\x00"+b"\x00"*8)
            put32(c,o,offset)
            c.reg_write(A.UC_ARM_REG_R0,0 if missing_text else t)
            c.reg_write(A.UC_ARM_REG_R1,0 if missing_offset else o)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_text_decode_489c5e"] if compiled else 0x489c5e
            c.emu_start(entry|1,0x600000,count=10000)
            return c.reg_read(A.UC_ARM_REG_R0),get32(c,o)
        patterns=[b"",b"A",b"\x7f",b"\x80",b"\xbf",b"\xc0",b"\xc2\xa2",
                  b"\xc2A",b"\xe2",b"\xe2\x82",b"\xe2\x82\xac",b"\xe2A\xac",
                  b"\xf0",b"\xf0\x9f",b"\xf0\x9f\x98",b"\xf0\x9f\x98\x80",
                  b"\xf0\x9fA\x80",b"\xf8",b"\xff"]
        patterns += [bytes([b]) for b in range(256)]
        cases=[(raw,offset,False,False) for raw,offset in itertools.product(patterns,(0,2))]
        cases += [(b"ABC",0,True,False),(b"ABC",0,False,True)]
        for case in cases:
            stock,source=run(False,case),run(True,case)
            if stock!=source:raise AssertionError((case,stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x489c5e..0x489dbb",
             "cases":len(cases),"limits":["Static UTF-8 decoder behavior is native compared; caller callback-cell placement remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
