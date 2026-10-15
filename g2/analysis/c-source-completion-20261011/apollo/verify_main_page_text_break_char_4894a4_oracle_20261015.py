#!/usr/bin/env python3
"""Compare Apollo line-break punctuation table with stock."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_text_break_char_4894a4.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-break-char-4894a4"
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    if blob[0x78b528-0x438000:0x78b534-0x438000]!=b" ,.;:-_)]}\x00\x00":
        raise RuntimeError("line-break table changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_text_is_break_char_4894a4",
                        str(SRC),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
              if len(p:=line.split())==3}
        with elf.open("rb") as f:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(f).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,glyph):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for a,d in segments:c.mem_write(a,d)
            c.mem_map(0x20000000,0x10000)
            c.reg_write(A.UC_ARM_REG_R0,glyph)
            c.reg_write(A.UC_ARM_REG_SP,0x2000f000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_text_is_break_char_4894a4"] if compiled else 0x4894a4
            c.emu_start(entry|1,0x600000,count=10000)
            return c.reg_read(A.UC_ARM_REG_R0)
        cases=list(range(256))+[0x100+x for x in range(256)]+[0x1f600,0xffffffff]
        for glyph in cases:
            stock,source=run(False,glyph),run(True,glyph)
            if stock!=source:raise AssertionError((hex(glyph),stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_BREAK_CHAR_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x4894a4..0x4894cf",
             "table_address":"0x78b528","cases":len(cases),
             "limits":["Table lookup is native compared; line segment traversal remains open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
