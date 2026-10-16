#!/usr/bin/env python3
"""Bind stock-compared audio index tables and zero-tail wrapper."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/audio_app_hardware_indices_20261016.c'
BASE=G2/'build/c-firmware/20261016/main-audio-app-hardware-core/apollo-main-audio-app-hardware-core-bound.o'
OUT=G2/'build/c-firmware/20261016/main-audio-app-hardware-indices';ORACLE=OUT/'oracle-receipt.json'
PROVIDERS={'audio_app_format_index_590d74','audio_app_rate_index_590d3c','audio_app_zero_tail_4d4ccc'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_AUDIO_APP_HARDWARE_INDICES_C_ORACLE' or oracle['cases']!=114 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('indices oracle changed')
 obj=OUT/'audio_app_hardware_indices_20261016.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=PROVIDERS:raise RuntimeError('indices providers changed')
 before=names(BASE,'-u')
 if len(before)!=175 or not PROVIDERS.issubset(before):raise RuntimeError('indices base changed')
 linked=OUT/'apollo-main-audio-app-hardware-indices-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!=PROVIDERS or after-before or len(after)!=172:raise RuntimeError(f'indices frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_AUDIO_APP_HARDWARE_INDICES_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':175,'unresolved_after':172,'imports_resolved':sorted(PROVIDERS),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Final RAM placement, lower-call side effects, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],175,172,sha(path))
if __name__=='__main__':main()
