#!/usr/bin/env python3
"""Bind stock-checked manual brightness and ALS scale getter."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_manual_brightness_46c1c8.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-manual-brightness-46c1c8/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-brightness-refresh-46c18c/apollo-main-setting-brightness-refresh-46c18c.o"
OUT=G2/"build/c-firmware/20261015/main-setting-manual-brightness-46c1c8"
OWNED={"audio_setting_als_scale_get_4ae946","audio_setting_manual_brightness_46c1c8"}
ADDED={"audio_als_manual_set_brightness_4ae81c"}
IMPORTS={"audio_als_manual_set_brightness_4ae81c","audio_als_scale_active",
         "audio_quicklist_tick_now","audio_setting_brightness_refresh_46c18c",
         "audio_settings_config_live","audio_uart_hand_mismatch_448e34"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_MANUAL_BRIGHTNESS_46C1C8" or oracle["cases"]!=147 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Manual brightness evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"setting_manual_brightness_46c1c8.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Manual brightness object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=195 or OWNED&before or ADDED&before or \
    not (IMPORTS-ADDED)<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Manual brightness base contract changed")
 linked=OUT/"apollo-main-setting-manual-brightness-46c1c8.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after or after-before!=ADDED or len(after)!=196:
  raise RuntimeError("Manual brightness link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_MANUAL_BRIGHTNESS_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "native_getter_sha256":oracle["native_getter_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":[],"imports_added":sorted(ADDED),
          "unresolved_before":195,"unresolved_after":196,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The bound manual path exposes stock ALS learning callee 0x4ae81c; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],195,196,sha(path))
if __name__=="__main__":main()
