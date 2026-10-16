#!/usr/bin/env python3
"""Bind stock-compared EvenAI display control to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/even_ai_display_ctrl_4e1fd2.c'
BASE=G2/'build/c-firmware/20261016/main-even-ai-ancc-state-sync/apollo-main-even-ai-ancc-state-sync-bound.o'
OUT=G2/'build/c-firmware/20261016/main-even-ai-display-ctrl';ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_EVEN_AI_DISPLAY_CTRL_C_ORACLE' or oracle['cases']!=7560 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('display ctrl oracle changed')
 obj=OUT/'even_ai_display_ctrl_4e1fd2.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_even_ai_display_ctrl_4e1fd2'}:raise RuntimeError('display ctrl provider changed')
 before=names(BASE,'-u')
 if len(before)!=170 or 'audio_even_ai_display_ctrl_4e1fd2' not in before:raise RuntimeError('display ctrl base changed')
 linked=OUT/'apollo-main-even-ai-display-ctrl-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_even_ai_display_ctrl_4e1fd2'} or after-before or len(after)!=169:raise RuntimeError(f'display ctrl frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_EVEN_AI_DISPLAY_CTRL_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':170,'unresolved_after':169,'imports_resolved':['audio_even_ai_display_ctrl_4e1fd2'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Display/alert/logger side effects, whole-image link and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],170,169,sha(path))
if __name__=='__main__':main()
