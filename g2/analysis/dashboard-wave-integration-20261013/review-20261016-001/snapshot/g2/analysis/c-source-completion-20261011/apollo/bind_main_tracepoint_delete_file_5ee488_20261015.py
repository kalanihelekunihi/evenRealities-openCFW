#!/usr/bin/env python3
"""Bind native-backed tracepoint single-file deletion handler into Main."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_delete_file_5ee488.c'
ORACLE_SCRIPT=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_delete_file_5ee488_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-delete-file-5ee488';ORACLE=OUT/'oracle.json'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-pb-descriptor-77cd84/apollo-main-tracepoint-pb-descriptor-77cd84.o'
OWNED={'audio_tracepoint_delete_file_5ee488'}
ADDED={'audio_tracepoint_validate_file_name_5ede30','audio_tracepoint_resolve_file_path_5eddf6','audio_tracepoint_storage_lock_47e088','audio_tracepoint_storage_unlink_47498c'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines()}
def main():
 subprocess.run([sys.executable,str(ORACLE_SCRIPT)],check=True,capture_output=True,text=True)
 oracle=json.loads(ORACLE.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_DELETE_FILE_NATIVE_C' or oracle['native_c_cases']!=120 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('delete-file oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_delete_file_5ee488.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!=OWNED:raise RuntimeError('source definitions changed')
 before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-delete-file-5ee488.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 after=names(linked,'-u')
 if len(before)!=191 or before-after!=OWNED or after-before!=ADDED or len(after)!=194:raise RuntimeError((len(before),len(after),before-after,after-before))
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DELETE_FILE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'oracle':str(ORACLE.relative_to(ROOT)),'oracle_sha256':sha(ORACLE),'native_c_cases':120,'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),'source_owned_symbols':sorted(OWNED),'unresolved_before':191,'unresolved_after':194,'imports_resolved':sorted(OWNED),'imports_added':sorted(ADDED),'source_complete':False,'full_payload_linked':False,'hardware_proof':False,'limits':['Four validator/storage children remain imports; effects checked only at call boundaries.','Final layout and hardware filesystem behavior unproved.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
