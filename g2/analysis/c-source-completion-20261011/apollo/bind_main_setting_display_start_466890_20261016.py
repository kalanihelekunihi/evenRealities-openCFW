#!/usr/bin/env python3
"""Bind stock-checked setting display-start selector before its parents."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_display_start_466890.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-display-start-466890/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-type9-467206/apollo-main-setting-type9-467206.o"
OUT=G2/"build/c-firmware/20261015/main-setting-display-start-466890"
OWNED={"audio_setting_display_start_466890"}
IMPORTS={"audio_settings_terminal_mode","audio_uart_master_display_start"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_DISPLAY_START_466890" or oracle["cases"]!=6 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Setting display-start evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"setting_display_start_466890.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Setting display-start object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=199 or OWNED&before or not IMPORTS<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Setting display-start base contract changed")
 linked=OUT/"apollo-main-setting-display-start-466890.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if after!=before:
  raise RuntimeError("Setting display-start link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_DISPLAY_START_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":[],
          "unresolved_before":199,"unresolved_after":199,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["This provider is bound ahead of its type-2 and type-3 callers; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],199,199,sha(path))
if __name__=="__main__":main()
