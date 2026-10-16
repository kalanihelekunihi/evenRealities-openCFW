#!/usr/bin/env python3
"""Bind checked onboarding startup check and source-owned flag getter."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/onboarding_check_start_46805a.c"
ORACLE=G2/"build/c-firmware/20261016/main-onboarding-start-46805a/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-wear-detect-status-49ebb6/apollo-main-wear-detect-status-49ebb6.o"
OUT=G2/"build/c-firmware/20261015/main-onboarding-start-46805a"
OWNED={"audio_onboarding_flag_get_4a7832","audio_wear_child_46805a"}
RESOLVED={"audio_wear_child_46805a"}
IMPORTS={"audio_log_extended","audio_log_flags","audio_log_wake_allowed",
         "audio_quicklist_refresh_enabled_4434d0","audio_uart_master_display_start",
         "compressed_log_output","g2_onboarding_flag"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_ONBOARDING_START_46805A" or oracle["cases"]!=84 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Onboarding startup evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"onboarding_check_start_46805a.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Onboarding startup object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=204 or not RESOLVED<=before or not IMPORTS<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Onboarding startup base contract changed")
 linked=OUT/"apollo-main-onboarding-start-46805a.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=RESOLVED or after-before or len(after)!=203:
  raise RuntimeError("Onboarding startup link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_ONBOARDING_START_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "native_getter_body_sha256":oracle["native_getter_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(RESOLVED),
          "imports_added":[],"unresolved_before":204,"unresolved_after":203,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["Onboarding startup uses existing C display providers; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],204,203,sha(path))
if __name__=="__main__":main()
