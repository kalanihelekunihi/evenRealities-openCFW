#!/usr/bin/env python3
"""Bind stock-compared ANCC display wrapper to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_ancc_display_clear_4e1af8.c'
BASE=G2/'build/c-firmware/20261016/main-even-ai-sync-remote/apollo-main-even-ai-sync-remote-bound.o'
OUT=G2/'build/c-firmware/20261016/main-even-ai-ancc-display-clear';ORACLE=OUT/'oracle-receipt.json'
CHILDREN={'audio_even_ai_ancc_display_send_5105bc','g2_audio_ancc_display_context_20073f84'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_EVEN_AI_ANCC_DISPLAY_CLEAR_C_ORACLE' or oracle['cases']!=42 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('display wrapper oracle changed')
 obj=OUT/'even_ai_ancc_display_clear_4e1af8.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_even_ai_ancc_display_clear_4e1af8'}:raise RuntimeError('display wrapper provider changed')
 before=names(BASE,'-u')
 if len(before)!=172 or 'audio_even_ai_ancc_display_clear_4e1af8' not in before:raise RuntimeError('display wrapper base changed')
 linked=OUT/'apollo-main-even-ai-ancc-display-clear-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_even_ai_ancc_display_clear_4e1af8'} or after-before!=CHILDREN or len(after)!=173:raise RuntimeError(f'display wrapper frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_EVEN_AI_ANCC_DISPLAY_CLEAR_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':172,'unresolved_after':173,'imports_resolved':['audio_even_ai_ancc_display_clear_4e1af8'],'imports_added':sorted(CHILDREN),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Display context extent, child send behavior, final placement, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],172,173,sha(path))
if __name__=='__main__':main()
