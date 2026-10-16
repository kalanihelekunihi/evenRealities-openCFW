#!/usr/bin/env python3
"""Bind three native-compared page event helper bodies into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
HERE=Path(__file__).resolve().parent
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_event_helpers_450286.c"
OUT=G2/"build/c-firmware/20261015/main-page-event-helpers-450286"
BASE=G2/"build/c-firmware/20261015/main-page-metric-getters-499360/apollo-main-page-metric-getters-499360.o"
ORACLE=HERE/"verify_main_page_event_helpers_450286_oracle_20261015.py"
RESOLVED={"audio_uart_page_event_code_450286","audio_uart_page_event_extent_4519fa",
          "audio_uart_page_event_prepare_49aacc"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def imports(p):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm","-u",str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_page_event_helpers_450286.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    subprocess.run([sys.executable,str(ORACLE)],check=True,capture_output=True,text=True)
    oracle=json.loads((OUT/"oracle.json").read_text())
    if oracle["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_HELPERS_ORACLE" or \
            oracle["cases"]!=47 or oracle["source_sha256"]!=sha(SOURCE):
        raise RuntimeError("page event helpers oracle changed")
    linked=OUT/"apollo-main-page-event-helpers-450286.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=imports(BASE),imports(linked)
    if before-after!=RESOLVED or after-before or len(before)!=240 or len(after)!=237:
        raise RuntimeError("page event helpers import contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_HELPERS_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"oracle_sha256":sha(OUT/"oracle.json"),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(RESOLVED),"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":oracle["limits"]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
