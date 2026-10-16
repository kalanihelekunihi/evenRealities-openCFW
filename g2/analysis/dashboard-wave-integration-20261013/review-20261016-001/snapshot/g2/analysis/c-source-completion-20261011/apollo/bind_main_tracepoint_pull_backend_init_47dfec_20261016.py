#!/usr/bin/env python3
"""Bind stock Main tracepoint backend initialization to C-owned state."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_backend_init_47dfec.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_pull_backend_init_47dfec_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-backend-init-47dfec'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-write-state-47df28/apollo-main-tracepoint-write-state-47df28.o'
ADDED={'audio_tracepoint_storage_mkdir_474a76','audio_tracepoint_read_state_47df8a','audio_tracepoint_file_size_47de7a'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_PULL_BACKEND_INIT_NATIVE_C' or oracle['native_c_cases']!=216 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('backend oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_pull_backend_init_47dfec.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_tracepoint_pull_backend_init_47dfec'} or names(obj,'-u')-names(BASE,'--defined-only')!=ADDED:raise RuntimeError('backend source contract changed')
 linked=OUT/'apollo-main-tracepoint-pull-backend-init-47dfec.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=193 or len(after)!=195 or before-after!={'audio_tracepoint_pull_backend_init_47dfec'} or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_BACKEND_INIT_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':216,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_tracepoint_pull_backend_init_47dfec'],
      'unresolved_before':193,'unresolved_after':195,
      'imports_resolved':['audio_tracepoint_pull_backend_init_47dfec'],'imports_added':sorted(ADDED),
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['216 controlled native/C backend-init cases; mkdir/state-read/file-size children, layout and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
