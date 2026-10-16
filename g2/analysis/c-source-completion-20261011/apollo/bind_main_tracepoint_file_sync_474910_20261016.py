#!/usr/bin/env python3
"""Bind stock 0x474910 stream sync facade, retaining its legacy caller name."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_sync_474910.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_file_sync_474910_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-file-sync-474910'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-file-open-474550/apollo-main-tracepoint-file-open-474550.o'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_FILE_SYNC_NATIVE_C' or oracle['native_c_cases']!=30 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('file-sync oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_file_sync_474910.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 expected={'audio_file_mutex_acquire','audio_file_mutex_release','audio_file_lfs_sync_4cfb08','audio_file_errno_location_439cc4','audio_file_api_mutex'}
 if names(obj,'--defined-only')!={'audio_tracepoint_file_close_474910'} or names(obj,'-u')!=expected:raise RuntimeError('file-sync C source contract changed')
 linked=OUT/'apollo-main-tracepoint-file-sync-474910.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=192 or len(after)!=192 or before-after!={'audio_tracepoint_file_close_474910'} or after-before!={'audio_file_lfs_sync_4cfb08'}:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_SYNC_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':30,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_tracepoint_file_close_474910'],
      'unresolved_before':192,'unresolved_after':192,
      'imports_resolved':['audio_tracepoint_file_close_474910'],'imports_added':['audio_file_lfs_sync_4cfb08'],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['30 native/C stream-sync cases; LittleFS sync child, final image and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
