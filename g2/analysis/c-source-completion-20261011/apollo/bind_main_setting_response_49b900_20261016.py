#!/usr/bin/env python3
"""Bind native-checked APP response serializer and bounded command RAM into Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_respond_to_app_serialize_49b900.c"
RAM=G2/"components/audio/uart_thread_source_candidate/settings_response_command_id_ram.c"
ORACLE=G2/"build/c-firmware/20261016/main-setting-response-49b900/oracle-receipt.json"
BASE=G2/"build/c-firmware/20261015/main-setting-data-recv-466976/apollo-main-setting-data-recv-466976.o"
OUT=G2/"build/c-firmware/20261015/main-setting-response-49b900"
OWNED={"audio_setting_serialize_response_49b900","audio_settings_response_command_id_20074860"}
RESOLVED={"audio_setting_serialize_response_49b900"}
ADDED={"audio_setting_response_encode_49b3d4"}
IMPORTS=ADDED|{"audio_uart_device_role_get","audio_uart_buffer_zero","audio_log_flags",
               "audio_log_extended","compressed_log_output","audio_ring_pb_tx_ble_475b14",
               "audio_settings_notify_encode_buffer","audio_settings_response_command_id_20074860"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(["arm-none-eabi-nm","-g",flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle["status"]!="PASS_NATIVE_MAIN_SETTING_RESPONSE_49B900" or oracle["cases"]!=180 or \
    oracle["source_sha256"]!=sha(SOURCE) or oracle["ram_source_sha256"]!=sha(RAM) or \
    oracle["official_payload_sha256"]!="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
  raise RuntimeError("Setting response evidence changed")
 OUT.mkdir(parents=True,exist_ok=True)
 objs=[]
 for source in (SOURCE,RAM):
  obj=OUT/(source.stem+".o")
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra",
                  "-Werror","-c",str(source),"-o",str(obj)],check=True)
  objs.append(obj)
 if symbols(objs[0],"--defined-only")!={"audio_setting_serialize_response_49b900"} or \
    symbols(objs[0],"-u")!=IMPORTS or \
    symbols(objs[1],"--defined-only")!={"audio_settings_response_command_id_20074860"} or \
    symbols(objs[1],"-u"):
  raise RuntimeError("Setting response object contract changed")
 before=symbols(BASE,"-u")
 if len(before)!=192 or not RESOLVED<=before or \
    not (IMPORTS-ADDED-{"audio_settings_response_command_id_20074860"})<=symbols(BASE,"--defined-only"):
  raise RuntimeError("Setting response base contract changed")
 linked=OUT/"apollo-main-setting-response-49b900.o"
 subprocess.run(["arm-none-eabi-ld","-r",str(BASE),*(str(o) for o in objs),"-o",str(linked)],check=True)
 after=symbols(linked,"-u")
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=192:
  raise RuntimeError("Setting response link delta changed")
 receipt={"status":"PASS_EXPERIMENTAL_MAIN_SETTING_RESPONSE_C",
          "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
          "ram_source":str(RAM.relative_to(ROOT)),"ram_source_sha256":sha(RAM),
          "oracle":str(ORACLE.relative_to(ROOT)),"oracle_sha256":sha(ORACLE),
          "oracle_cases":oracle["cases"],"native_body_sha256":oracle["native_body_sha256"],
          "objects":[{"path":str(o.relative_to(ROOT)),"sha256":sha(o)} for o in objs],
          "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
          "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
          "source_owned_symbols":sorted(OWNED),"imports_resolved":sorted(RESOLVED),
          "imports_added":sorted(ADDED),"unresolved_before":192,"unresolved_after":192,
          "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
          "limits":["Response encoder is an explicit import; four-byte command RAM has unknown startup value and surrounding allocation; final layout and hardware remain open."]}
 path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
 print(receipt["status"],192,192,sha(path))
if __name__=="__main__":main()
