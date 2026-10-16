#!/usr/bin/env python3
"""Bind stock public LittleFS sync wrapper to existing C lower providers."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/file_lfs_sync_4cfb08.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_file_lfs_sync_4cfb08_20261016.py'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-sync-4cfb08'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-file-sync-474910/apollo-main-tracepoint-file-sync-474910.o'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {s.split()[-1] for s in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if s.strip()}
def main():
 subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
 oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
 if oracle['status']!='PASS_BOUNDED_MAIN_FILE_LFS_SYNC_NATIVE_C' or oracle['native_c_cases']!=32 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('LittleFS sync oracle changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'file_lfs_sync_4cfb08.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 expected={'g2_lfs_mlist_isopen','g2_file_close_error','g2_lfs_file_sync'}
 if names(obj,'--defined-only')!={'audio_file_lfs_sync_4cfb08'} or names(obj,'-u')!=expected or not expected<=names(BASE,'--defined-only'):raise RuntimeError('LittleFS sync C source contract changed')
 linked=OUT/'apollo-main-file-lfs-sync-4cfb08.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
 before=names(BASE,'-u');after=names(linked,'-u')
 if len(before)!=192 or len(after)!=191 or before-after!={'audio_file_lfs_sync_4cfb08'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
 row={'status':'PASS_EXPERIMENTAL_MAIN_FILE_LFS_SYNC_C',
      'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
      'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':32,
      'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
      'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
      'source_owned_symbols':['audio_file_lfs_sync_4cfb08'],
      'unresolved_before':192,'unresolved_after':191,
      'imports_resolved':['audio_file_lfs_sync_4cfb08'],'imports_added':[],
      'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
      'limits':['32 native/C public LittleFS sync cases; final image and hardware remain open.']}
 path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
 print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
