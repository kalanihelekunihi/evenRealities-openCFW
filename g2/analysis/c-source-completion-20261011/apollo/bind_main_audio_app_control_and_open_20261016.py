#!/usr/bin/env python3
"""Bind stock-compared audio packet queue and hardware-open wrapper."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_control_and_open_20261016.c'
BASE=G2/'build/c-firmware/20261016/main-audio-app-setup-children/apollo-main-audio-app-setup-children-bound.o'
OUT=G2/'build/c-firmware/20261016/main-audio-app-control-and-open';ORACLE=OUT/'oracle-receipt.json'
PROVIDERS={'audio_app_control_packet_53c638','audio_app_hardware_open_591374','g2_audio_control_context_20003f98'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_AUDIO_APP_CONTROL_AND_OPEN_C_ORACLE' or oracle['cases']!=126 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('control oracle changed')
 obj=OUT/'audio_app_control_and_open_20261016.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=PROVIDERS:raise RuntimeError('control providers changed')
 before=names(BASE,'-u')
 if len(before)!=174 or not {'audio_app_control_packet_53c638','audio_app_hardware_open_591374'}.issubset(before):raise RuntimeError('control base changed')
 linked=OUT/'apollo-main-audio-app-control-and-open-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 resolved={'audio_app_control_packet_53c638','audio_app_hardware_open_591374'}
 if before-after!=resolved or after-before!={'audio_app_hardware_core_59123a'} or len(after)!=173:raise RuntimeError(f'control frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_AUDIO_APP_CONTROL_AND_OPEN_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':174,'unresolved_after':173,'imports_resolved':sorted(resolved),'imports_added':['audio_app_hardware_core_59123a'],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Hardware core, final RAM placement, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],174,173,sha(path))
if __name__=='__main__':main()
