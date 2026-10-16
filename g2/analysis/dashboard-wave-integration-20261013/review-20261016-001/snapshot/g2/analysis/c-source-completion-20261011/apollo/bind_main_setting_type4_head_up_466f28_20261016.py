#!/usr/bin/env python3
"""Bind stock-checked type-4 head-up dispatcher and expose config child."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/setting_type4_head_up_466f28.c'
ORACLE=G2/'build/c-firmware/20261016/main-setting-type4-head-up-466f28/oracle-receipt.json'
BASE=G2/'build/c-firmware/20261015/main-setting-type1-brightness-466bec/apollo-main-setting-type1-brightness-466bec.o'
OUT=G2/'build/c-firmware/20261015/main-setting-type4-head-up-466f28'
OWNED={'audio_setting_dispatch_type4_466f28'}
ADDED={'audio_setting_head_up_configure_46c524'}
IMPORTS={'audio_log_extended','audio_log_flags','audio_setting_head_up_configure_46c524',
         'audio_settings_get_config_46b44c','audio_settings_notify_recalibration_status_49beac',
         'audio_system_alert_close_464c36','audio_uart_calibration_status_2007501c',
         'audio_uart_master_display_start','audio_uart_service_mode','compressed_log_output'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_NATIVE_MAIN_SETTING_TYPE4_HEAD_UP_466F28' or oracle['cases']!=1260 or \
    oracle['source_sha256']!=sha(SOURCE) or \
    oracle['official_payload_sha256']!='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
  raise RuntimeError('Type-4 head-up evidence changed')
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/'setting_type4_head_up_466f28.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra',
                 '-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if symbols(obj,'--defined-only')!=OWNED or symbols(obj,'-u')!=IMPORTS:
  raise RuntimeError('Type-4 head-up object contract changed')
 before=symbols(BASE,'-u');provided=symbols(BASE,'--defined-only')
 if len(before)!=194 or before&OWNED!=OWNED or ADDED&before or \
    not (IMPORTS-ADDED)<=provided:
  raise RuntimeError('Type-4 head-up base contract changed')
 linked=OUT/'apollo-main-setting-type4-head-up-466f28.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=OWNED or after-before!=ADDED or len(after)!=194:
  raise RuntimeError('Type-4 head-up link frontier changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_SETTING_TYPE4_HEAD_UP_C',
          'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
          'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),
          'oracle_cases':oracle['cases'],'native_body_sha256':oracle['native_body_sha256'],
          'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),
          'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
          'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
          'source_owned_symbols':sorted(OWNED),'imports_resolved':sorted(OWNED),
          'imports_added':sorted(ADDED),'unresolved_before':194,'unresolved_after':194,
          'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
          'limits':['The native head-up config callee 0x46c524 remains exposed; final layout and hardware behavior remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],194,194,sha(path))
if __name__=='__main__':main()
