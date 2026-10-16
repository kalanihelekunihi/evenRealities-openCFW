#!/usr/bin/env python3
"""Bind the bounded tracepoint tp_<decimal>.bin parser into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_parse_sequence_5edaf0.c'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_parse_sequence_5edaf0_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-parse-sequence-5edaf0';ORACLE=OUT/'oracle.json'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-resolve-file-path-5eddf6/apollo-main-tracepoint-resolve-file-path-5eddf6.o'
OWNED={'audio_tracepoint_parse_sequence_5edaf0'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_SEQUENCE_PARSER_NATIVE_C' or oracle['native_c_cases']!=45 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('sequence-parser oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_parse_sequence_5edaf0.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('sequence parser definitions changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-parse-sequence-5edaf0.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=194 or len(after)!=193 or before-after!=OWNED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SEQUENCE_PARSER_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':45,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':194,'unresolved_after':193,'imports_resolved':sorted(OWNED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['String and number providers are simulated at call boundaries; full filesystem behavior and hardware unproved.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
