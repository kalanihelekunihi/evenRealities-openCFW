#!/usr/bin/env python3
"""Bind stock-compared ANCC state packet sender to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_ancc_state_sync_497cf0.c'
BASE=G2/'build/c-firmware/20261016/main-even-ai-ancc-display-send/apollo-main-even-ai-ancc-display-send-bound.o'
OUT=G2/'build/c-firmware/20261016/main-even-ai-ancc-state-sync';ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_EVEN_AI_ANCC_STATE_SYNC_C_ORACLE' or oracle['cases']!=42 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('state sync oracle changed')
 obj=OUT/'even_ai_ancc_state_sync_497cf0.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_even_ai_ancc_state_sync_497cf0'}:raise RuntimeError('state sync provider changed')
 before=names(BASE,'-u')
 if len(before)!=171 or 'audio_even_ai_ancc_state_sync_497cf0' not in before:raise RuntimeError('state sync base changed')
 linked=OUT/'apollo-main-even-ai-ancc-state-sync-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_even_ai_ancc_state_sync_497cf0'} or after-before or len(after)!=170:raise RuntimeError(f'state sync frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_EVEN_AI_ANCC_STATE_SYNC_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':171,'unresolved_after':170,'imports_resolved':['audio_even_ai_ancc_state_sync_497cf0'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Paired-send side effects, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],171,170,sha(path))
if __name__=='__main__':main()
