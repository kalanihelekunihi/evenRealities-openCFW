#!/usr/bin/env python3
"""Bind file-directory facades and bounded shared result buffer to Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_dir_facade_474b02.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_dir_result_200701e8.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_dir_facade_474b02_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-dir-facade-474b02'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-reset-pull-478110/apollo-main-tracepoint-reset-pull-478110.o'
OWNED={'audio_tracepoint_dir_open_474b02','audio_tracepoint_dir_read_474bb8',
       'audio_tracepoint_dir_close_474c66','audio_tracepoint_dir_result_200701e8'}
RESOLVED=OWNED-{'audio_tracepoint_dir_result_200701e8'}
EXPECTED={'audio_file_api_mutex','audio_file_errno_location_439cc4','audio_file_heap_free',
          'audio_file_lfs_context','audio_file_lfs_dir_close_4cfcf8','audio_file_lfs_dir_open_4cfc66',
          'audio_file_lfs_dir_read_4cfd02','audio_file_mutex_acquire','audio_file_mutex_release',
          'audio_file_ready_200746a8','audio_settings_copy_text','codec_allocate'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*args):return subprocess.check_output(args,text=True)
def names(p,flag):return {line.split()[-1] for line in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_DIR_FACADE_NATIVE_C' or oracle['native_c_cases']!=162 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('directory oracle changed')
    if '0x200701e8 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('directory result placement changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_dir_facade_474b02.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!=EXPECTED:raise RuntimeError('directory source contract changed')
    sections=out('arm-none-eabi-readelf','-SW',str(obj))
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.dir_result\s+NOBITS\s+',line) and '000101' in line for line in sections.splitlines()):raise RuntimeError('directory NOBITS extent changed')
    placed=OUT/'tracepoint-dir-result-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_dir_result_200701e8')!=0x200701e8:raise RuntimeError('directory result address changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-dir-facade-474b02.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=194 or len(after)!=191 or before-after!=RESOLVED or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DIR_FACADE_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':162,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_address':'0x200701e8','section_bytes':0x101,'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':194,'unresolved_after':191,
         'imports_resolved':sorted(RESOLVED),'imports_added':[],
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Directory facade passed 162 controlled native/C cases; actual filesystem storage and final RAM layout remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
