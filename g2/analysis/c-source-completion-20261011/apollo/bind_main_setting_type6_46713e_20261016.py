#!/usr/bin/env python3
"""Bind stock-checked setting type-6 silent-mode route."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_dispatch_type6_46713e.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-type6-46713e/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-settings-input-check-46b0ec/apollo-main-settings-input-check-46b0ec.o"
OUT=G2/"build/c-firmware/20261015/main-setting-type6-46713e"
OWNED={"audio_setting_dispatch_type6_46713e"}
RESOLVED=OWNED
ADDED={"audio_silent_mode_set_from_app_46921c"}
IMPORTS={"audio_log_flags","audio_log_extended","compressed_log_output"}|ADDED
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_TYPE6_46713E" or oracle["cases"]!=30 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Setting type-6 evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"setting_dispatch_type6_46713e.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Setting type-6 object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=201 or not RESOLVED<=before or \
    not (IMPORTS-ADDED)<=symbols(BASE,"--defined-only") or ADDED&before:
  raise RuntimeError("Setting type-6 base contract changed")
 linked=OUT/"apollo-main-setting-type6-46713e.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=201:
  raise RuntimeError("Setting type-6 link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_TYPE6_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(RESOLVED),
          "imports_added":sorted(ADDED),"unresolved_before":201,"unresolved_after":201,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The type-6 body exposes stock silent-mode child 0x46921c; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],201,201,sha(path))
if __name__=="__main__":main()
