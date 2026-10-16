#!/usr/bin/env python3
"""Bind native-checked local-data response serializer into Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_respond_local_serialize_49ba58.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-local-response-49ba58/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-response-encode-49b3d4/apollo-main-setting-response-encode-49b3d4.o"
OUT=G2/"build/c-firmware/20261015/main-setting-local-response-49ba58"
OWNED={"audio_setting_serialize_local_response_49ba58"}
ADDED={"audio_setting_local_response_encode_49b7c4"}
IMPORTS=ADDED|{"audio_uart_device_role_get","audio_uart_buffer_zero","audio_log_flags",
               "audio_log_extended","compressed_log_output","audio_ring_pb_tx_ble_475b14",
               "audio_settings_notify_encode_buffer","audio_settings_response_command_id_20074860"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_LOCAL_RESPONSE_49BA58" or oracle["cases"]!=180 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Setting local response evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"setting_respond_local_serialize_49ba58.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=IMPORTS:
  raise RuntimeError("Setting local response object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=191 or not OWNED<=before or \
    not (IMPORTS-ADDED)<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Setting local response base contract changed")
 linked=OUT/"apollo-main-setting-local-response-49ba58.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=OWNED or after-before!=ADDED or len(after)!=191:
  raise RuntimeError("Setting local response link delta changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_LOCAL_RESPONSE_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
          "imports_added":sorted(ADDED),"unresolved_before":191,"unresolved_after":191,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["Local-data encoder remains an explicit import; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],191,191,sha(path))
if __name__=="__main__":main()
