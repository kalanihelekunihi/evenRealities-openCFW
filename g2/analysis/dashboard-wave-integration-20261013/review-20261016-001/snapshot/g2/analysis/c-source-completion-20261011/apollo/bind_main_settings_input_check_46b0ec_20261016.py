#!/usr/bin/env python3
"""Bind stock-checked settings input-event gate and wear predicate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/settings_input_event_check_46b0ec.c"
ORACLE=G2/"build/c-firmware/20261016/main-settings-input-check-46b0ec/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-wear-child-51308a/apollo-main-wear-child-51308a.o"
OUT=G2/"build/c-firmware/20261015/main-settings-input-check-46b0ec"
OWNED={"audio_wear_child_46b0ec","audio_wear_input_enabled_49eb96"}
RESOLVED={"audio_wear_child_46b0ec"}
IMPORTS={"audio_log_extended","audio_log_flags","audio_ota_transfer_active",
         "audio_settings_get_config_46b44c","audio_uart_case_status",
         "audio_uart_command_pending","audio_uart_lcd_status_cell",
         "audio_wear_detect_get_enable_49ead8","compressed_log_output"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTINGS_INPUT_CHECK_46B0EC" or oracle["cases"]!=252 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Settings input-check evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"settings_input_event_check_46b0ec.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Settings input-check object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=202 or not RESOLVED<=before or not IMPORTS<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Settings input-check base contract changed")
 linked=OUT/"apollo-main-settings-input-check-46b0ec.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=RESOLVED or after-before or len(after)!=201:
  raise RuntimeError("Settings input-check link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTINGS_INPUT_CHECK_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "native_helper_body_sha256":oracle["native_helper_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(RESOLVED),
          "imports_added":[],"unresolved_before":202,"unresolved_after":201,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The gate uses existing C state providers; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],202,201,sha(path))
if __name__=="__main__":main()
