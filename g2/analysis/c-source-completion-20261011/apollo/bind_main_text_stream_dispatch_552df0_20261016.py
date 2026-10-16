#!/usr/bin/env python3
"""Bind stock-compared text-stream dispatch and prefix child to Apollo Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261016/main-text-stream-restart/apollo-main-text-stream-restart-bound.o'
OUT=G2/'build/c-firmware/20261016/main-text-stream-dispatch'
PREFIX_OUT=G2/'build/c-firmware/20261016/main-text-stream-prefix-match'
DISPATCH=G2/'components/audio/uart_thread_source_candidate/text_stream_dispatch_552df0.c'
PREFIX=G2/'components/audio/uart_thread_source_candidate/text_stream_prefix_match_552ecc.c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def checked(path,source,status,cases):
    r=json.loads(path.read_text())
    if r['status']!=status or r['cases']!=cases or r['source_sha256']!=sha(source):raise RuntimeError('oracle receipt changed: '+str(path))
    return r
def main():
    checked(PREFIX_OUT/'oracle-receipt.json',PREFIX,'PASS_EXPERIMENTAL_TEXT_STREAM_PREFIX_MATCH_C_ORACLE',121)
    checked(OUT/'oracle-receipt.json',DISPATCH,'PASS_EXPERIMENTAL_TEXT_STREAM_DISPATCH_C_ORACLE',336)
    before=names(BASE,'-u')
    if len(before)!=174 or 'audio_text_stream_dispatch_552df0' not in before:raise RuntimeError('Apollo dispatch base changed')
    objs=[]
    for source,name in ((PREFIX,'audio_text_stream_prefix_match_552ecc'),(DISPATCH,'audio_text_stream_dispatch_552df0')):
        obj=OUT/(source.stem+'.o')
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
        if names(obj,'--defined-only')!={name}:raise RuntimeError('provider symbols changed: '+str(obj))
        objs.append(obj)
    linked=OUT/'apollo-main-text-stream-dispatch-bound.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*(str(p) for p in objs),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if before-after!={'audio_text_stream_dispatch_552df0'} or after-before!={'audio_text_stream_begin_552f0a','audio_text_stream_finish_552f14'} or len(after)!=175:raise RuntimeError(f'Apollo dispatch frontier changed: {before-after}, {after-before}')
    receipt={'status':'PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_DISPATCH_C','source':str(DISPATCH.relative_to(ROOT)),'source_sha256':sha(DISPATCH),'prefix_source':str(PREFIX.relative_to(ROOT)),'prefix_source_sha256':sha(PREFIX),'oracle_receipt':str((OUT/'oracle-receipt.json').relative_to(ROOT)),'oracle_receipt_sha256':sha(OUT/'oracle-receipt.json'),'prefix_oracle_receipt':str((PREFIX_OUT/'oracle-receipt.json').relative_to(ROOT)),'prefix_oracle_receipt_sha256':sha(PREFIX_OUT/'oracle-receipt.json'),'objects':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in objs],'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'unresolved_before':174,'unresolved_after':175,'imports_resolved':['audio_text_stream_dispatch_552df0'],'imports_added':['audio_text_stream_begin_552f0a','audio_text_stream_finish_552f14'],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Controlled oracle models lower calls; callback path and lower-call side effects remain open.','Whole-image link and hardware execution remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(receipt['status'],174,175,sha(path))
if __name__=='__main__':main()
