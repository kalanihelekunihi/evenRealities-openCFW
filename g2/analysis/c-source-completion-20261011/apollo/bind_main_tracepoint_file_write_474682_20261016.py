#!/usr/bin/env python3
"""Bind stock redirect fwrite to existing Apollo C providers."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_write_474682.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_file_write_474682_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-write-474682'
BASE=G2/'build/c-firmware/20261015/main-file-lfs-sync-4cfb08/apollo-main-file-lfs-sync-4cfb08.o'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_FILE_WRITE_NATIVE_C' or oracle['native_c_cases']!=75 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('file-write oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_file_write_474682.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 expected={'audio_file_api_mutex','audio_file_lfs_write_4cfb7c','audio_file_mutex_acquire','audio_file_mutex_release','audio_log_extended','audio_log_flags','compressed_log_output'}
 if names(obj,'--defined-only')!={'audio_tracepoint_file_write_474682'} or names(obj,'-u')!=expected or not expected<=names(BASE,'--defined-only'):raise RuntimeError('file-write C source contract changed')
 linked=OUT/'apollo-main-tracepoint-file-write-474682.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=191 or len(after)!=190 or before-after!={'audio_tracepoint_file_write_474682'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_WRITE_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':75,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_tracepoint_file_write_474682'],
      'unresolved_before':191,'unresolved_after':190,
      'imports_resolved':['audio_tracepoint_file_write_474682'],'imports_added':[],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['75 native/C fwrite cases including five logging masks; full image and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
