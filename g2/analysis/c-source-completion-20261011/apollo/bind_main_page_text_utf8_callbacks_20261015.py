#!/usr/bin/env python3
"""Bind six UTF-8 callback bodies and table neighbors around decoder cell."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
DIR=G2/"components/audio/uart_thread_source_candidate"
OUT=G2/"build/c-firmware/20261015/main-page-text-utf8-callbacks"
BASE=G2/"build/c-firmware/20261015/main-page-text-decode-cell-78f2a4/apollo-main-page-text-decode-cell-78f2a4.o"
PARTS=(
    ("display_page_text_utf8_length_489b74.c","verify_main_page_text_utf8_length_489b74_oracle_20261015.py","main-page-text-utf8-length-489b74",256,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_LENGTH_ORACLE"),
    ("display_page_text_utf8_encode_489bac.c","verify_main_page_text_utf8_encode_489bac_oracle_20261015.py","main-page-text-utf8-encode-489bac",594,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_ENCODE_ORACLE"),
    ("display_page_text_utf8_traversal_489dbc.c","verify_main_page_text_utf8_traversal_489dbc_oracle_20261015.py","main-page-text-utf8-traversal-489dbc",122,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_TRAVERSAL_ORACLE"),
)
TABLE=DIR/"display_page_text_utf8_callback_neighbors.c"
NATIVE=(0x489b75,0x489bad,0x489c5f,0x489dbd,0x489e15,0x489e4b,0x489e6f)
CALLBACKS=("audio_uart_text_utf8_length_489b74","audio_uart_text_utf8_encode_489bac",
           "audio_uart_text_utf8_previous_489dbc","audio_uart_text_utf8_bytes_for_count_489e14",
           "audio_uart_text_utf8_count_to_bytes_489e4a","audio_uart_text_utf8_count_489e6e")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*cmd):return subprocess.check_output(cmd,text=True)
def imports(p):return {s.split()[-1] for s in run("arm-none-eabi-nm","-u",str(p)).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo payload changed")
    words=tuple(int.from_bytes(blob[a-0x438000:a-0x438000+4],"little")
                for a in range(0x78f29c,0x78f2b8,4))
    if words!=NATIVE:raise RuntimeError("UTF-8 callback table changed")
    objects=[];sources=[];oracles=[]
    for name,script_name,dirname,count,status in PARTS:
        source=DIR/name;script=HERE/script_name
        subprocess.run([sys.executable,str(script)],check=True,capture_output=True,text=True)
        oracle_path=G2/"build/c-firmware/20261015"/dirname/"oracle.json"
        oracle=json.loads(oracle_path.read_text())
        if oracle["status"]!=status or oracle["cases"]!=count or \
                oracle["source_sha256"]!=sha(source):
            raise RuntimeError(("UTF-8 callback oracle changed",name))
        obj=OUT/(source.stem+".o")
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                        "-Wextra","-Werror","-c",str(source),"-o",str(obj)],check=True)
        objects.append(obj)
        sources.append({"path":str(source.relative_to(ROOT)),"sha256":sha(source),
                        "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj)})
        oracles.append({"path":str(oracle_path.relative_to(ROOT)),"sha256":sha(oracle_path)})
    table_obj=OUT/"display_page_text_utf8_callback_neighbors.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(TABLE),"-o",str(table_obj)],check=True)
    relocs=run("arm-none-eabi-readelf","-rW",str(table_obj))
    sections=run("arm-none-eabi-readelf","-SW",str(table_obj))
    if relocs.count("R_ARM_ABS32")!=6 or \
            not all(name in relocs for name in CALLBACKS) or \
            ".g2_rom_78f29c" not in sections or ".g2_rom_78f2a8" not in sections:
        raise RuntimeError("UTF-8 callback table relocations changed")
    linked=OUT/"apollo-main-page-text-utf8-callbacks.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),*(str(o) for o in objects),
                    str(table_obj),"-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before!=after or len(before)!=235:
        raise RuntimeError(("UTF-8 callback import contract changed",before-after,after-before))
    defined=run("arm-none-eabi-nm","--defined-only",str(linked))
    if not all(name in defined for name in CALLBACKS):
        raise RuntimeError("UTF-8 callback definitions missing")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_CALLBACKS_C",
             "sources":sources,"oracle_receipts":oracles,
             "table_source":str(TABLE.relative_to(ROOT)),"table_source_sha256":sha(TABLE),
             "table_object_sha256":sha(table_obj),
             "native_table_start":"0x78f29c","native_thumb_words":[hex(w) for w in words],
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":[],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Seven callback bodies and cells have source ownership; final contiguous ROM placement, malformed traversal, full image link, and hardware behavior remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
