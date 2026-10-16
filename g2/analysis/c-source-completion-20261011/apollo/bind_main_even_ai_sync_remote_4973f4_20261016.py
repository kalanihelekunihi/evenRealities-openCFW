#!/usr/bin/env python3
"""Bind stock-compared ANCC clear/sync body to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_sync_remote_4973f4.c'
BASE=G2/'build/c-firmware/20261016/main-audio-app-hardware-indices/apollo-main-audio-app-hardware-indices-bound.o'
OUT=G2/'build/c-firmware/20261016/main-even-ai-sync-remote';ORACLE=OUT/'oracle-receipt.json'
PROVIDERS={'audio_even_ai_sync_remote_4973f4','g2_audio_ancc_records_20104c54','g2_audio_ancc_sequence_20074918'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_EVEN_AI_SYNC_REMOTE_C_ORACLE' or oracle['cases']!=60 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('sync oracle changed')
 obj=OUT/'even_ai_sync_remote_4973f4.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=PROVIDERS:raise RuntimeError('sync providers changed')
 before=names(BASE,'-u')
 if len(before)!=172 or 'audio_even_ai_sync_remote_4973f4' not in before:raise RuntimeError('sync base changed')
 linked=OUT/'apollo-main-even-ai-sync-remote-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_even_ai_sync_remote_4973f4'} or after-before!={'audio_even_ai_ancc_display_clear_4e1af8'} or len(after)!=172:raise RuntimeError(f'sync frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_EVEN_AI_SYNC_REMOTE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':172,'unresolved_after':172,'imports_resolved':['audio_even_ai_sync_remote_4973f4'],'imports_added':['audio_even_ai_ancc_display_clear_4e1af8'],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['ANCC display child, final RAM placement, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],172,172,sha(path))
if __name__=='__main__':main()
