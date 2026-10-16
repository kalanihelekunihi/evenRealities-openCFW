#!/usr/bin/env python3
"""Bind stock-checked type-1 brightness dispatcher."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/setting_type1_brightness_466bec.c'
ORACLE=G2/'build/c-firmware/20261016/main-setting-type1-brightness-466bec/oracle-receipt.json'
BASE=G2/'build/c-firmware/20261015/main-als-manual-target-scale-4addb6/apollo-main-als-manual-target-scale-4addb6.o'
OUT=G2/'build/c-firmware/20261015/main-setting-type1-brightness-466bec'
OWNED={'audio_setting_dispatch_type1_466bec'}
IMPORTS={'audio_log_extended','audio_log_flags','audio_setting_brightness_refresh_46c18c',
         'audio_setting_manual_brightness_46c1c8','audio_settings_get_config_46b44c',
         'audio_uart_auto_brightness_configure','compressed_log_output'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_NATIVE_MAIN_SETTING_TYPE1_BRIGHTNESS_466BEC' or oracle['cases']!=200 or \
    oracle['source_sha256']!=sha(SOURCE) or \
    oracle['official_payload_sha256']!='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
  raise RuntimeError('Type-1 brightness evidence changed')
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/'setting_type1_brightness_466bec.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra',
                 '-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if symbols(obj,'--defined-only')!=OWNED or symbols(obj,'-u')!=IMPORTS:
  raise RuntimeError('Type-1 brightness object contract changed')
 before=symbols(BASE,'-u');provided=symbols(BASE,'--defined-only')
 if len(before)!=195 or before&OWNED!=OWNED or not IMPORTS<=provided:
  raise RuntimeError('Type-1 brightness base contract changed')
 linked=OUT/'apollo-main-setting-type1-brightness-466bec.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=OWNED or after-before or len(after)!=194:
  raise RuntimeError('Type-1 brightness link frontier changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_SETTING_TYPE1_BRIGHTNESS_C',
          'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
          'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),
          'oracle_cases':oracle['cases'],'native_body_sha256':oracle['native_body_sha256'],
          'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),
          'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
          'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
          'source_owned_symbols':sorted(OWNED),'imports_resolved':sorted(OWNED),
          'imports_added':[],'unresolved_before':195,'unresolved_after':194,
          'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
          'limits':['Type-1 route uses existing C brightness and config providers; final layout and hardware behavior remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],195,194,sha(path))
if __name__=='__main__':main()
