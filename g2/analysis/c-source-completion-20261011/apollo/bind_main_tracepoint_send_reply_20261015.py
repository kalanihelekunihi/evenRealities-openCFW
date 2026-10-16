#!/usr/bin/env python3
"""Bind stock-backed tracepoint phone/master send children into Main archive."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_send_reply_5edfd8_5ee066.c'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_send_reply_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-send-reply-5edfd8-5ee066'
ORACLE=OUT/'oracle.json';BASE=G2/'build/c-firmware/20261015/main-tracepoint-reply-result-5ee134/apollo-main-tracepoint-reply-result-5ee134.o'
OWNED={'audio_tracepoint_send_to_phone_5edfd8','audio_tracepoint_send_to_master_5ee066'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_SEND_REPLY_NATIVE_C' or oracle['native_c_cases']!=540 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_send_reply_5edfd8_5ee066.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('definitions changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-send-reply-5edfd8-5ee066.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u');resolved=before-after;added=after-before
 if len(before)!=194 or resolved!=OWNED or added!={'audio_tracepoint_encode_response_5eded0','audio_tracepoint_encoded_buffer'}:raise RuntimeError((len(before),len(after),resolved,added))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SEND_REPLY_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':540,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':len(before),'unresolved_after':len(after),'imports_resolved':sorted(resolved),'imports_added':sorted(added),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Response encoder and bounded encoded buffer remain imports; final placement and hardware unproved.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
