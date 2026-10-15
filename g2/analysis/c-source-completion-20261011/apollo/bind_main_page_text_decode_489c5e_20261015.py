#!/usr/bin/env python3
"""Bind native-compared Apollo UTF-8 decoding into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_text_decode_489c5e.c"
OUT=G2/"build/c-firmware/20261015/main-page-text-decode-489c5e"
BASE=G2/"build/c-firmware/20261015/main-page-text-line-length-4897fc/apollo-main-page-text-line-length-4897fc.o"
ORACLE=HERE/"verify_main_page_text_decode_489c5e_oracle_20261015.py"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm","-u",str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_text_decode_489c5e.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_ORACLE" or \
            oracle["cases"]!=552 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("text decoder oracle changed")
    linked=OUT/"apollo-main-page-text-decode-489c5e.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before-after!={"audio_uart_text_decode_489c5e"} or after-before or \
            len(before)!=239 or len(after)!=238:
        raise RuntimeError(("text decoder import contract changed",before-after,after-before,len(before),len(after)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":["audio_uart_text_decode_489c5e"],"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":oracle["limits"]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
