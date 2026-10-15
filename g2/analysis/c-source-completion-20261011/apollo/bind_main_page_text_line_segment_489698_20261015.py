#!/usr/bin/env python3
"""Bind native-compared Apollo line segment and its three local helpers."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE_DIR=G2/"components/audio/uart_thread_source_candidate"
OUT=G2/"build/c-firmware/20261015/main-page-text-line-segment-489698"
BASE=G2/"build/c-firmware/20261015/main-page-font-resource-aliases/apollo-main-page-font-resource-aliases.o"
PARTS=(
    ("display_page_text_line_segment_489698.c","verify_main_page_text_line_segment_489698_oracle_20261015.py",437,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_SEGMENT_ORACLE","main-page-text-line-segment-489698"),
    ("display_page_text_hash_state_489652.c","verify_main_page_text_hash_state_489652_oracle_20261015.py",1536,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_HASH_STATE_ORACLE","main-page-text-hash-state-489652"),
    ("display_page_text_break_char_4894a4.c","verify_main_page_text_break_char_4894a4_oracle_20261015.py",514,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_BREAK_CHAR_ORACLE","main-page-text-break-char-4894a4"),
    ("display_page_text_cjk_4894d0.c","verify_main_page_text_cjk_4894d0_oracle_20261015.py",633,"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_CJK_ORACLE","main-page-text-cjk-4894d0"),
)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm","-u",str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    objects=[];sources=[];oracle_receipts=[]
    for name,script_name,count,status,dirname in PARTS:
        source=SOURCE_DIR/name
        script=HERE/script_name
        subprocess.run([sys.executable,str(script)],check=True,capture_output=True,text=True)
        receipt_path=G2/"build/c-firmware/20261015"/dirname/"oracle.json"
        oracle=json.loads(receipt_path.read_text())
        if oracle["status"]!=status or oracle["cases"]!=count or \
                oracle["source_sha256"]!=sha(source):
            raise RuntimeError(("line segment provider oracle changed",name))
        obj=OUT/(source.stem+".o")
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                        "-Wextra","-Werror","-c",str(source),"-o",str(obj)],check=True)
        objects.append(obj);sources.append({"path":str(source.relative_to(ROOT)),"sha256":sha(source),
                                             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj)})
        oracle_receipts.append({"path":str(receipt_path.relative_to(ROOT)),"sha256":sha(receipt_path)})
    linked=OUT/"apollo-main-page-text-line-segment-489698.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),*(str(o) for o in objects),
                    "-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before-after!={"audio_uart_text_line_segment_489698"} or after-before or \
            len(before)!=236 or len(after)!=235:
        raise RuntimeError(("line segment import contract changed",before-after,after-before,len(before),len(after)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_SEGMENT_C",
             "sources":sources,"oracle_receipts":oracle_receipts,
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":["audio_uart_text_line_segment_489698"],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Line segment uses controlled glyph advance; full font and hardware rendering remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
