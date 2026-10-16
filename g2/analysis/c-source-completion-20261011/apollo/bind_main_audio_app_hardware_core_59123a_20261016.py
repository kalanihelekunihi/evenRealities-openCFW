#!/usr/bin/env python3
"""Bind stock-compared audio hardware descriptor builder to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_hardware_core_59123a.c'
BASE=G2/'build/c-firmware/20261016/main-audio-app-control-and-open/apollo-main-audio-app-control-and-open-bound.o'
OUT=G2/'build/c-firmware/20261016/main-audio-app-hardware-core';ORACLE=OUT/'oracle-receipt.json'
CHILDREN={'audio_app_rate_index_590d3c','audio_app_format_index_590d74','audio_app_zero_tail_4d4ccc'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_AUDIO_APP_HARDWARE_CORE_C_ORACLE' or oracle['cases']!=1728 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('hardware core oracle changed')
 obj=OUT/'audio_app_hardware_core_59123a.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_app_hardware_core_59123a'}:raise RuntimeError('hardware core provider changed')
 before=names(BASE,'-u')
 if len(before)!=173 or 'audio_app_hardware_core_59123a' not in before:raise RuntimeError('hardware core base changed')
 linked=OUT/'apollo-main-audio-app-hardware-core-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_app_hardware_core_59123a'} or after-before!=CHILDREN or len(after)!=175:raise RuntimeError(f'hardware core frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_AUDIO_APP_HARDWARE_CORE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':173,'unresolved_after':175,'imports_resolved':['audio_app_hardware_core_59123a'],'imports_added':sorted(CHILDREN),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Index helpers, tail-zero side effects, final placement, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],173,175,sha(path))
if __name__=='__main__':main()
