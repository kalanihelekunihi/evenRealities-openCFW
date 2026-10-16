#!/usr/bin/env python3
"""Bind stock-checked ALS manual learning body and four RAM cells."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/als_manual_brightness_4ae81c.c'
ORACLE=G2/'build/c-firmware/20261016/main-als-manual-brightness-4ae81c/oracle-receipt.json'
BASE=G2/'build/c-firmware/20261015/main-setting-manual-brightness-46c1c8/apollo-main-setting-manual-brightness-46c1c8.o'
OUT=G2/'build/c-firmware/20261015/main-als-manual-brightness-4ae81c'
OWNED={'audio_als_manual_set_brightness_4ae81c','audio_als_manual_ready',
       'audio_als_manual_level','audio_als_manual_level_copy','audio_als_manual_pending'}
RESOLVED={'audio_als_manual_set_brightness_4ae81c'}
ADDED={'audio_als_manual_set_target_4ade36','audio_als_manual_recalculate_4adcd8'}
IMPORTS={'audio_als_active_previous','audio_als_apply_previous','audio_als_curve_adjusted',
         'audio_als_default_previous','audio_als_manual_set_target_4ade36',
         'audio_als_manual_recalculate_4adcd8','audio_als_scale_active',
         'audio_log_extended','audio_log_flags','compressed_log_output'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_NATIVE_MAIN_ALS_MANUAL_BRIGHTNESS_4AE81C' or oracle['cases']!=240 or \
    oracle['source_sha256']!=sha(SOURCE) or \
    oracle['official_payload_sha256']!='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
  raise RuntimeError('ALS manual brightness evidence changed')
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/'als_manual_brightness_4ae81c.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra',
                 '-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if symbols(obj,'--defined-only')!=OWNED or symbols(obj,'-u')!=IMPORTS:
  raise RuntimeError('ALS manual brightness object contract changed')
 before=symbols(BASE,'-u');provided=symbols(BASE,'--defined-only')
 if len(before)!=196 or before&OWNED!=RESOLVED or ADDED&before or \
    not (IMPORTS-ADDED)<=provided:
  raise RuntimeError('ALS manual brightness base contract changed')
 linked=OUT/'apollo-main-als-manual-brightness-4ae81c.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=RESOLVED or after-before!=ADDED or len(after)!=197:
  raise RuntimeError('ALS manual brightness link frontier changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_ALS_MANUAL_BRIGHTNESS_C',
          'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
          'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),
          'oracle_cases':oracle['cases'],'native_body_sha256':oracle['native_body_sha256'],
          'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),
          'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
          'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
          'source_owned_symbols':sorted(OWNED),'imports_resolved':sorted(RESOLVED),
          'imports_added':sorted(ADDED),'unresolved_before':196,'unresolved_after':197,
          'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
          'limits':['The ALS learner exposes stock target and recalculate helpers; four RAM cells need final placement.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],196,197,sha(path))
if __name__=='__main__':main()
