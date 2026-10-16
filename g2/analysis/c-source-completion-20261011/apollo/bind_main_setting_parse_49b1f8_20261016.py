#!/usr/bin/env python3
"""Bind stock-checked setting parser, duplicate helper and bounded RAM cell."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
DIR=G2/"components/audio/uart_thread_source_candidate"
SOURCES=(DIR/"setting_parse_data_package_49b1f8.c",
         DIR/"setting_duplicate_message_49b198.c",
         DIR/"settings_last_received_magic_ram.c")
ORACLES=(G2/"build/c-firmware/20261016/main-setting-parse-49b1f8/oracle-receipt.json",
         G2/"build/c-firmware/20261016/main-setting-duplicate-49b198/oracle-receipt.json")
BASE=G2/"build/c-firmware/20261015/main-setting-local-response-encode-49b7c4/apollo-main-setting-local-response-encode-49b7c4.o"
OUT=G2/"build/c-firmware/20261015/main-setting-parse-49b1f8"
OWNED={"audio_setting_parse_data_package_49b1f8",
       "audio_setting_is_duplicate_message_49b198",
       "audio_settings_last_received_magic_20074868"}
RESOLVED={"audio_setting_parse_data_package_49b1f8"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 first,second=(json.loads(p.read_text()) for p in ORACLES)
 if first["status"]!="PASS_NATIVE_MAIN_SETTING_PARSE_49B1F8" or first["cases"]!=320 or \
    first["source_sha256"]!=sha(SOURCES[0]) or \
    second["status"]!="PASS_NATIVE_MAIN_SETTING_DUPLICATE_49B198" or second["cases"]!=128 or \
    second["source_sha256"]!=sha(SOURCES[1]) or second["ram_source_sha256"]!=sha(SOURCES[2]) or \
    {first["official_payload_sha256"],second["official_payload_sha256"]}!={"19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"}:
  raise RuntimeError("Setting parser evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 objects=[]
 for source in SOURCES:
  obj=OUT/(source.stem+".o")
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                  "-Werror","-c",str(source),"-o",str(obj)],check=True)
  objects.append(obj)
 if set().union(*(symbols(o,"--defined-only") for o in objects))!=OWNED:
  raise RuntimeError("Setting parser owned symbols changed")
 before=symbols(BASE,"-u")
 combined=set().union(*(symbols(o,"-u") for o in objects))
 if len(before)!=190 or not RESOLVED<=before or not (combined-OWNED)<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Setting parser base contract changed")
 linked=OUT/"apollo-main-setting-parse-49b1f8.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),*(str(o) for o in objects),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=RESOLVED or after-before or len(after)!=189:
  raise RuntimeError("Setting parser link frontier changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_PARSE_C",
          "source":str(SOURCES[0].relative_to(ROOT)),"source_sha256":sha(SOURCES[0]),
          "sources":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in SOURCES],
          "oracles":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p),"cases":d["cases"],
                      "native_body_sha256":d["native_body_sha256"]} for p,d in zip(ORACLES,(first,second))],
          "objects":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in objects],
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(RESOLVED),
          "imports_added":[],"unresolved_before":190,"unresolved_after":189,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["Parser and duplicate helper use existing C nanopb and log providers; RAM startup value, final placement and hardware behavior remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],190,189,sha(path))
if __name__=="__main__":main()
