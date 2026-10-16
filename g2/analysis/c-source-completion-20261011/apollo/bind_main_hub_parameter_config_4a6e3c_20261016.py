#!/usr/bin/env python3
"""Bind stock-checked HUB parameter dispatcher and expose three children."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/hub_parameter_config_4a6e3c.c'
ORACLE=G2/'build/c-firmware/20261016/main-hub-parameter-config-4a6e3c/oracle-receipt.json'
BASE=G2/'build/c-firmware/20261015/main-setting-head-up-configure-46c524/apollo-main-setting-head-up-configure-46c524.o'
OUT=G2/'build/c-firmware/20261015/main-hub-parameter-config-4a6e3c'
OWNED={'audio_hub_parameter_config_4a6e3c'}
ADDED={'audio_hub_semantic_motion_threshold_4a4e8c',
       'audio_hub_semantic_motion_period_4a4ec0','audio_hub_imu_accel_config_4a52a2'}
IMPORTS=ADDED|{'audio_log_extended','audio_log_flags','audio_uart_hub_role_cell',
               'compressed_log_output'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_NATIVE_MAIN_HUB_PARAMETER_CONFIG_4A6E3C' or oracle['cases']!=405 or \
    oracle['source_sha256']!=sha(SOURCE) or \
    oracle['official_payload_sha256']!='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
  raise RuntimeError('HUB parameter evidence changed')
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/'hub_parameter_config_4a6e3c.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra',
                 '-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if symbols(obj,'--defined-only')!=OWNED or symbols(obj,'-u')!=IMPORTS:
  raise RuntimeError('HUB parameter object contract changed')
 before=symbols(BASE,'-u');provided=symbols(BASE,'--defined-only')
 if len(before)!=194 or before&OWNED!=OWNED or ADDED&before or \
    not (IMPORTS-ADDED)<=provided:
  raise RuntimeError('HUB parameter base contract changed')
 linked=OUT/'apollo-main-hub-parameter-config-4a6e3c.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=OWNED or after-before!=ADDED or len(after)!=196:
  raise RuntimeError('HUB parameter link frontier changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_HUB_PARAMETER_CONFIG_C',
          'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
          'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),
          'oracle_cases':oracle['cases'],'native_body_sha256':oracle['native_body_sha256'],
          'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),
          'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
          'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
          'source_owned_symbols':sorted(OWNED),'imports_resolved':sorted(OWNED),
          'imports_added':sorted(ADDED),'unresolved_before':194,'unresolved_after':196,
          'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
          'limits':['Three stock motion or IMU child calls remain exposed; final layout and hardware behavior remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],194,196,sha(path))
if __name__=='__main__':main()
