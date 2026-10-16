#!/usr/bin/env python3
"""Bind pinned-source LittleFS directory drop to Apollo Main."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_file_lfs_dir_drop_4cc5a2.c'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_file_lfs_dir_drop_4cc5a2_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-file-lfs-dir-drop-4cc5a2'
BASE=G2/'build/c-firmware/20261015/main-file-lfs-remove-core-4ce4dc/apollo-main-file-lfs-remove-core-4ce4dc.o'
OWNED={'audio_file_lfs_dir_drop_4cc5a2'};EXPECTED={'g2_lfs_dir_getgstate','g2_lfs_dir_commit'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def names(p,flag):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-g',flag,str(p)],text=True).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_FILE_LFS_DIR_DROP_NATIVE_C' or oracle['native_c_cases']!=8 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('dir-drop oracle changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'display_file_lfs_dir_drop_4cc5a2.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!=EXPECTED:raise RuntimeError('dir-drop source contract changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-file-lfs-dir-drop-4cc5a2.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=191 or len(after)!=190 or before-after!=OWNED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_FILE_LFS_DIR_DROP_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':8,
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':191,'unresolved_after':190,
         'imports_resolved':sorted(OWNED),'imports_added':[],
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Directory drop passed eight controlled native/C cases; whole NOR filesystem state and image placement remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
