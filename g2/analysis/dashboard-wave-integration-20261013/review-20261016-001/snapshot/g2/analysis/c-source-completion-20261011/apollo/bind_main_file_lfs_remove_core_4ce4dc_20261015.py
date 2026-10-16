#!/usr/bin/env python3
"""Bind stock/pinned-source LittleFS remove core to Apollo Main."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_file_lfs_remove_core_4ce4dc.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_file_lfs_remove_core_4ce4dc_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-remove-core-4ce4dc'
BASE=G2/'build/c-firmware/20261015/main-file-lfs-remove-wrapper-4cfa76/apollo-main-file-lfs-remove-wrapper-4cfa76.o'
OWNED={'audio_file_lfs_remove_core_4ce4dc'};ADDED={'audio_file_lfs_dir_drop_4cc5a2'}
EXPECTED={'audio_file_lfs_ctz_fromle32','audio_file_lfs_dir_find','audio_file_lfs_dir_get',
          'audio_file_lfs_forceconsistency','g2_lfs_dir_commit','g2_lfs_dir_fetch',
          'g2_lfs_fs_pred','g2_lfs_fs_preporphans'}|ADDED
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_FILE_LFS_REMOVE_CORE_NATIVE_C' or oracle['native_c_cases']!=40 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('remove-core oracle changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'display_file_lfs_remove_core_4ce4dc.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!=EXPECTED:raise RuntimeError('remove-core source contract changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-file-lfs-remove-core-4ce4dc.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=191 or len(after)!=191 or before-after!=OWNED or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_FILE_LFS_REMOVE_CORE_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':40,
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':191,'unresolved_after':191,
         'imports_resolved':sorted(OWNED),'imports_added':sorted(ADDED),
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Remove control flow passed 40 bounded native/C cases with controlled callees. Full NOR side effects and directory-drop child remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
