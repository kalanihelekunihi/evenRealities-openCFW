#!/usr/bin/env python3
"""Bind source-owned Apollo UTF-8 decoder callback cell."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_decode_cell_78f2a4.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-decode-cell-78f2a4"
BASE=G2/"build/c-firmware/20261015/main-page-text-line-segment-489698/apollo-main-page-text-line-segment-489698.o"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*cmd):return subprocess.check_output(cmd,text=True)
def imports(p):return {s.split()[-1] for s in run("arm-none-eabi-nm","-u",str(p)).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    stock=int.from_bytes(blob[0x78f2a4-0x438000:0x78f2a8-0x438000],"little")
    if stock!=0x489c5f:raise RuntimeError("decoder callback cell changed")
    obj=OUT/"display_page_text_decode_cell_78f2a4.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    sections=run("arm-none-eabi-readelf","-SW",str(obj))
    relocs=run("arm-none-eabi-readelf","-rW",str(obj))
    symbols=run("arm-none-eabi-readelf","-sW",str(obj))
    if ".g2_rom_78f2a4" not in sections or \
            "R_ARM_ABS32" not in relocs or \
            "audio_uart_text_decode_489c5e" not in relocs or \
            "audio_uart_text_decode_cell_78f2a4" not in symbols:
        raise RuntimeError("decoder cell relocation contract changed")
    linked=OUT/"apollo-main-page-text-decode-cell-78f2a4.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before!=after or len(before)!=235 or \
            "audio_uart_text_decode_cell_78f2a4" not in run("arm-none-eabi-nm","--defined-only",str(linked)):
        raise RuntimeError("decoder cell linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_CELL_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"native_address":"0x78f2a4",
             "native_word":"0x489c5f","relocation":"R_ARM_ABS32 audio_uart_text_decode_489c5e",
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Cell bytes and relocation are source-owned; final ROM placement, adjacent callback table, and image link remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
