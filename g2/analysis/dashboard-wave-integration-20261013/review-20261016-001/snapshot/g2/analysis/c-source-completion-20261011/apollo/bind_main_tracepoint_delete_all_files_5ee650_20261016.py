#!/usr/bin/env python3
"""Bind stock tracepoint delete-all traversal recovered from the raw Main payload."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_delete_all_files_5ee650.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_delete_all_files_5ee650_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-delete-all-files-5ee650'
BASE=G2/'build/c-firmware/20261015/main-file-lfs-mkdir-core-4cd3aa/apollo-main-file-lfs-mkdir-core-4cd3aa.o'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_DELETE_ALL_FILES_NATIVE_C' or oracle['native_c_cases']!=70 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('delete-all oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_delete_all_files_5ee650.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 expected={'audio_log_extended','audio_log_flags','audio_tracepoint_dir_close_474c66','audio_tracepoint_dir_open_474b02','audio_tracepoint_dir_read_474bb8','audio_tracepoint_format_file_path_5edba2','audio_tracepoint_parse_sequence_5edaf0','audio_tracepoint_storage_lock_47e088','audio_tracepoint_storage_unlink_47498c','compressed_log_output'}
 if names(obj,'--defined-only')!={'audio_tracepoint_delete_all_files_5ee650'} or names(obj,'-u')!=expected or not expected<=names(BASE,'--defined-only'):raise RuntimeError('delete-all source contract changed')
 linked=OUT/'apollo-main-tracepoint-delete-all-files-5ee650.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=189 or len(after)!=188 or before-after!={'audio_tracepoint_delete_all_files_5ee650'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DELETE_ALL_FILES_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':70,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_tracepoint_delete_all_files_5ee650'],
      'unresolved_before':189,'unresolved_after':188,
      'imports_resolved':['audio_tracepoint_delete_all_files_5ee650'],'imports_added':[],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['70 bounded native/C traversal and logging cases; full image and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
