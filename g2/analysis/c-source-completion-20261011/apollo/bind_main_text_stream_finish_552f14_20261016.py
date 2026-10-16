#!/usr/bin/env python3
"""Bind stock-compared text-stream finish to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_finish_552f14.c'
BASE=G2/'build/c-firmware/20261016/main-text-stream-begin/apollo-main-text-stream-begin-bound.o'
OUT=G2/'build/c-firmware/20261016/main-text-stream-finish';ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_TEXT_STREAM_FINISH_C_ORACLE' or oracle['cases']!=1440 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('finish oracle changed')
 obj=OUT/'text_stream_finish_552f14.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_text_stream_finish_552f14'}:raise RuntimeError('finish provider changed')
 before=names(BASE,'-u')
 if len(before)!=175 or 'audio_text_stream_finish_552f14' not in before:raise RuntimeError('finish base changed')
 linked=OUT/'apollo-main-text-stream-finish-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_text_stream_finish_552f14'} or after-before or len(after)!=174:raise RuntimeError(f'finish frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_FINISH_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':175,'unresolved_after':174,'imports_resolved':['audio_text_stream_finish_552f14'],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Lower-call side effects, whole-image link, and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],175,174,sha(path))
if __name__=='__main__':main()
