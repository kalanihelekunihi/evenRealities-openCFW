#!/usr/bin/env python3
"""Bind native-compared LV text line selection into Apollo Main."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_line_length_4897fc.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-line-length-4897fc"
BASE=G2/"build/c-firmware/20261015/main-page-text-line-width-489934/apollo-main-page-text-line-width-489934.o"
ORACLE=HERE/"verify_main_page_text_line_length_4897fc_oracle_20261015.py"
RESOLVED={"audio_uart_text_line_length_4897fc"}
ADDED={"audio_uart_text_line_segment_489698","audio_uart_text_decode_489c5e"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm","-u",str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_text_line_length_4897fc.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_LENGTH_ORACLE" or \
            oracle["cases"]!=674 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("line length oracle changed")
    linked=OUT/"apollo-main-page-text-line-length-4897fc.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before-after!=RESOLVED or after-before!=ADDED or len(before)!=238 or len(after)!=239:
        raise RuntimeError(("line length import contract changed",before-after,after-before,len(before),len(after)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_LENGTH_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(RESOLVED),"imports_added":sorted(ADDED),
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":oracle["limits"]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
