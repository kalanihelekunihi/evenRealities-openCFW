#!/usr/bin/env python3
"""Bind the stock LittleFS mkdir wrapper and expose its core."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_lfs_mkdir_4cfc5c.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_file_lfs_mkdir_4cfc5c_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-mkdir-4cfc5c'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-storage-mkdir-474a76/apollo-main-tracepoint-storage-mkdir-474a76.o'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_FILE_LFS_MKDIR_WRAPPER_NATIVE_C' or oracle['native_c_cases']!=20 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('mkdir wrapper oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'file_lfs_mkdir_4cfc5c.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 if names(obj,'--defined-only')!={'audio_file_lfs_mkdir_4cfc5c'} or names(obj,'-u')!={'audio_file_lfs_mkdir_core_4cd3aa'}:raise RuntimeError('mkdir wrapper source contract changed')
 linked=OUT/'apollo-main-file-lfs-mkdir-4cfc5c.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=193 or len(after)!=193 or before-after!={'audio_file_lfs_mkdir_4cfc5c'} or after-before!={'audio_file_lfs_mkdir_core_4cd3aa'}:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_FILE_LFS_MKDIR_WRAPPER_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':20,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_file_lfs_mkdir_4cfc5c'],
      'unresolved_before':193,'unresolved_after':193,
      'imports_resolved':['audio_file_lfs_mkdir_4cfc5c'],'imports_added':['audio_file_lfs_mkdir_core_4cd3aa'],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['20 native/C wrapper cases; LittleFS mkdir core, layout and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
