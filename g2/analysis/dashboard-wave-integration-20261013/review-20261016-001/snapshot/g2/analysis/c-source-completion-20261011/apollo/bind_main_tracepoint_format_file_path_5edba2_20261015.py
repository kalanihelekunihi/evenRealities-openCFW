#!/usr/bin/env python3
"""Bind native-backed tracepoint bounded file path formatting wrapper."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_format_file_path_5edba2.c'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_format_file_path_5edba2_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-format-file-path-5edba2';ORACLE=OUT/'oracle.json'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-validate-file-name-5ede30/apollo-main-tracepoint-validate-file-name-5ede30.o'
OWNED={'audio_tracepoint_format_file_path_5edba2'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_PATH_FORMAT_NATIVE_C' or oracle['native_c_cases']!=25 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('path format oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_format_file_path_5edba2.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('path format definitions changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-format-file-path-5edba2.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=193 or len(after)!=192 or before-after!=OWNED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PATH_FORMAT_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':25,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':193,'unresolved_after':192,'imports_resolved':sorted(OWNED),'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Bounded format call verified; formatter provider body and hardware filesystem behavior remain separate evidence.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
