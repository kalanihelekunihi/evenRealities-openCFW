#!/usr/bin/env python3
"""Bind stock-checked IMU acceleration interval and RAM cell."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/hub_imu_accel_config_4a52a2.c'
ORACLE=G2/'build/c-firmware/20261016/main-hub-imu-accel-config-4a52a2/oracle-receipt.json'
BASE=G2/'build/c-firmware/20261015/main-hub-semantic-motion-period-4a4ec0/apollo-main-hub-semantic-motion-period-4a4ec0.o'
OUT=G2/'build/c-firmware/20261015/main-hub-imu-accel-config-4a52a2'
OWNED={'audio_hub_imu_accel_config_4a52a2','audio_hub_imu_report_interval_cell'}
RESOLVED={'audio_hub_imu_accel_config_4a52a2'}
IMPORTS={'audio_log_extended','audio_log_flags','compressed_log_output'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,flag):
 return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_NATIVE_MAIN_HUB_IMU_ACCEL_CONFIG_4A52A2' or oracle['cases']!=80 or \
    oracle['source_sha256']!=sha(SOURCE) or \
    oracle['official_payload_sha256']!='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701':
  raise RuntimeError('IMU acceleration evidence changed')
 OUT.mkdir(parents=True,exist_ok=True)
 obj=OUT/'hub_imu_accel_config_4a52a2.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra',
                 '-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if symbols(obj,'--defined-only')!=OWNED or symbols(obj,'-u')!=IMPORTS:
  raise RuntimeError('IMU acceleration object contract changed')
 before=symbols(BASE,'-u');provided=symbols(BASE,'--defined-only')
 if len(before)!=195 or before&OWNED!=RESOLVED or not IMPORTS<=provided:
  raise RuntimeError('IMU acceleration base contract changed')
 linked=OUT/'apollo-main-hub-imu-accel-config-4a52a2.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=symbols(linked,'-u')
 if before-after!=RESOLVED or after-before or len(after)!=194:
  raise RuntimeError('IMU acceleration link frontier changed')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_HUB_IMU_ACCEL_CONFIG_C',
          'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
          'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),
          'oracle_cases':oracle['cases'],'native_body_sha256':oracle['native_body_sha256'],
          'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),
          'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
          'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
          'source_owned_symbols':sorted(OWNED),'imports_resolved':sorted(RESOLVED),
          'imports_added':[],'unresolved_before':195,'unresolved_after':194,
          'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
          'limits':['The bounded IMU interval RAM cell needs final placement; motion threshold child remains open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],195,194,sha(path))
if __name__=='__main__':main()
