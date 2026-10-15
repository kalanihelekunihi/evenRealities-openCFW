#!/usr/bin/env python3
"""Compare Apollo non-rendering glyph predicate against stock."""
import hashlib,json,random,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SRC=G2/"components/audio/uart_thread_source_candidate/display_page_font_glyph_missing_4d559c.c"
OUT=G2/"build/c-firmware/20261015/main-page-font-glyph-missing-4d559c"
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest=hashlib.sha256(blob).hexdigest()
    if digest!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        elf=Path(td)/"oracle.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_font_glyph_is_missing_4d559c",
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
            entry=syms["audio_uart_font_glyph_is_missing_4d559c"] if compiled else 0x4d559c
            c.emu_start(entry|1,0x600000,count=10000)
            return c.reg_read(A.UC_ARM_REG_R0)
        cases=set(range(0x100))
        for value in (0x61c,0x115f,0x1160,0x180b,0x180f,0x200b,0x2010,
                      0x2028,0x2030,0x205f,0x2070,0xfeff,0xf8ff):
            cases.update(range(value-2,value+3))
        rng=random.Random(0x4d559c)
        cases.update(rng.randrange(0x110000) for _ in range(300))
        cases.update((0xffffffff,0x80000000,0x110000))
        for glyph in sorted(cases):
            stock,source=run(False,glyph),run(True,glyph)
            if stock!=source:raise AssertionError((hex(glyph),stock,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_MISSING_ORACLE",
             "source":str(SRC.relative_to(ROOT)),"source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
             "official_payload_sha256":digest,"native_span":"0x4d559c..0x4d5611",
             "cases":len(cases),"limits":["Predicate behavior is native compared; font descriptor and rendering behavior remain open."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(cases))
if __name__=="__main__":main()
