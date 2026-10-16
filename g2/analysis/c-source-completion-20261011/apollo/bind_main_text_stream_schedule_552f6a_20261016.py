#!/usr/bin/env python3
"""Bind stock-compared text-stream schedule body to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/text_stream_schedule_552f6a.c'
BASE=G2/'build/c-firmware/20261016/main-text-stream-finish/apollo-main-text-stream-finish-bound.o'
OUT=G2/'build/c-firmware/20261016/main-text-stream-schedule';ORACLE=OUT/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_EXPERIMENTAL_TEXT_STREAM_SCHEDULE_C_ORACLE' or oracle['cases']!=9600 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('schedule oracle changed')
 obj=OUT/'text_stream_schedule_552f6a.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_text_stream_schedule_552f6a'}:raise RuntimeError('schedule provider changed')
 before=names(BASE,'-u')
 if len(before)!=174 or 'audio_text_stream_schedule_552f6a' not in before:raise RuntimeError('schedule base changed')
 linked=OUT/'apollo-main-text-stream-schedule-bound.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if before-after!={'audio_text_stream_schedule_552f6a'} or after-before!={'audio_text_stream_tick_553054'} or len(after)!=174:raise RuntimeError(f'schedule frontier changed: {before-after}, {after-before}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_SCHEDULE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle_receipt':str(ORACLE.relative_to(ROOT)),'oracle_receipt_sha256':sha(ORACLE),'object':str(obj.relative_to(ROOT)),'object_sha256':sha(obj),'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':174,'unresolved_after':174,'imports_resolved':['audio_text_stream_schedule_552f6a'],'imports_added':['audio_text_stream_tick_553054'],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Timer callback, whole-image link, and hardware execution remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(receipt['status'],174,174,sha(path))
if __name__=='__main__':main()
