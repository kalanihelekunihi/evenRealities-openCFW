#!/usr/bin/env python3
"""Bind tracepoint file-size facade to existing Main file API."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_size_5edb68.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_file_size_5edb68_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-size-5edb68'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-scan-files-5edc5a/apollo-main-tracepoint-scan-files-5edc5a.o'
OWNED={'audio_tracepoint_file_size_5edb68'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_FILE_SIZE_NATIVE_C' or oracle['native_c_cases']!=30 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('file-size oracle changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_file_size_5edb68.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!={'audio_file_open','audio_file_seek','audio_file_tell','audio_file_close'}:raise RuntimeError('file-size symbols changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-file-size-5edb68.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=195 or len(after)!=194 or before-after!=OWNED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_SIZE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':30,
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':195,'unresolved_after':194,
         'imports_resolved':sorted(OWNED),'imports_added':[],
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['File size facade passed 30 controlled native/C cases; underlying filesystem and full image remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
