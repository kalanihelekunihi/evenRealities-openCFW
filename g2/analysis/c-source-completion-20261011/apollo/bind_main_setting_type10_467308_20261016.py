#!/usr/bin/env python3
"""Bind stock-checked setting type-10 gesture-list route."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_dispatch_type10_467308.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-type10-467308/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-gesture-apptype-46658e/apollo-main-setting-gesture-apptype-46658e.o"
OUT=G2/"build/c-firmware/20261015/main-setting-type10-467308"
OWNED={"audio_setting_dispatch_type10_467308"}
IMPORTS={"audio_log_extended","audio_log_flags","audio_setting_gesture_apptype_46658e",
         "audio_setting_unit_record_get_466010","audio_uart_ring_unpair_publish_hand_4661a6",
         "compressed_log_output"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_TYPE10_467308" or oracle["cases"]!=45 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Setting type-10 evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"setting_dispatch_type10_467308.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Setting type-10 object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=196 or not OWNED<=before or not IMPORTS<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Setting type-10 base contract changed")
 linked=OUT/"apollo-main-setting-type10-467308.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=OWNED or after-before or len(after)!=195:
  raise RuntimeError("Setting type-10 link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_TYPE10_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),"imports_added":[],
          "unresolved_before":196,"unresolved_after":195,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The list handler is controlled through the maximum one-byte count; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],196,195,sha(path))
if __name__=="__main__":main()
