#!/usr/bin/env python3
"""Bind checked 0x51308a request wrapper and expose its direct callee."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/wear_child_51308a.c"
ORACLE=G2/"build/c-firmware/20261016/main-wear-child-51308a/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-wear-child-502bf0/apollo-main-wear-child-502bf0.o"
OUT=G2/"build/c-firmware/20261015/main-wear-child-51308a"
OWNED={"audio_wear_child_51308a"}
ADDED=set()
PROVIDER="audio_input_message_send_record"
PROVIDER_SOURCE=G2/"components/audio/uart_thread_source_candidate/input_msg_send_record.c"
PROVIDER_RECEIPT=G2/"build/c-firmware/20261014/main-input-msg-record-corrected/receipt.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_WEAR_CHILD_51308A" or oracle["cases"]!=10 or \
    oracle["source_sha256"]!=sha(SOURCE) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Wear child evidence changed")
 provider=json.loads(PROVIDER_RECEIPT.read_text())
 if provider["status"]!="PASS_NATIVE_INPUT_MSG_RECORD_CORRECTED" or provider["cases"]!=24 or \
    provider["source_sha256"]!=sha(PROVIDER_SOURCE) or \
    provider["official_image_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Input-message provider evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/"wear_child_51308a.o"
 subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                 "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                 "-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
 if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!={PROVIDER}:
  raise RuntimeError("Wear child object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=203 or not OWNED<=before or PROVIDER not in symbols(BASE,"--defined-only"):
  raise RuntimeError("Wear child base contract changed")
 linked=OUT/"apollo-main-wear-child-51308a.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=OWNED or after-before!=ADDED or len(after)!=202:
  raise RuntimeError("Wear child link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_WEAR_CHILD_51308A_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "provider_source":str(PROVIDER_SOURCE.relative_to(ROOT)),
          "provider_source_sha256":sha(PROVIDER_SOURCE),
          "provider_oracle":str(PROVIDER_RECEIPT.relative_to(ROOT)),
          "provider_oracle_sha256":sha(PROVIDER_RECEIPT),
          "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(OWNED),
          "imports_added":sorted(ADDED),"unresolved_before":203,"unresolved_after":202,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["The callee is an existing native-checked C provider; final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],203,202,sha(path))
if __name__=="__main__":main()
