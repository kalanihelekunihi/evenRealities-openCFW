#!/usr/bin/env python3
"""Bind tracepoint file-list request, name formatter, and ready flag."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-insert-file-sorted-5edbb0/apollo-main-tracepoint-insert-file-sorted-5edbb0.o'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_request_file_name_5ee1f8.c'
FORMAT=G2/'components/audio/uart_thread_source_candidate/tracepoint_format_list_name_5eddc8.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_list_ready_20074ae4.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_request_file_name_5ee1f8_20261015.py'
FORMAT_VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_format_list_name_5eddc8_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-request-file-name-5ee1f8'
FORMAT_OUT=G2/'build/c-firmware/20261015/main-tracepoint-format-list-name-5eddc8/oracle.json'
OWNED={'audio_tracepoint_request_file_name_5ee1f8','audio_tracepoint_format_list_name_5eddc8','audio_tracepoint_local_file_list_ready'}
ADDED={'audio_tracepoint_reset_pull_478110','audio_tracepoint_prepare_pull_48ec9e','audio_tracepoint_scan_files_5edc5a'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*args):return subprocess.check_output(args,text=True)
def names(p,flag):return {line.split()[-1] for line in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if line.strip()}
def main():
    for script in (FORMAT_VERIFY,VERIFY):subprocess.run([sys.executable,str(script)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text());fmt=json.loads(FORMAT_OUT.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_REQUEST_FILE_NAME_NATIVE_C' or oracle['native_c_cases']!=64 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('request oracle changed')
    if fmt['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_LIST_NAME_NATIVE_C' or fmt['native_c_cases']!=64 or fmt['source_sha256']!=sha(FORMAT):raise RuntimeError('name oracle changed')
    if '0x20074ae4 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('ready placement changed')
    OUT.mkdir(parents=True,exist_ok=True);objects=[]
    for path in (FORMAT,SOURCE):
        obj=OUT/(path.stem+'.o')
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(path),'-o',str(obj)],check=True)
        objects.append(obj)
    if set().union(*(names(p,'--defined-only') for p in objects))!=OWNED:raise RuntimeError('request symbols changed')
    sections=out('arm-none-eabi-readelf','-SW',str(objects[1]))
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.file_list_ready\s+NOBITS\s+',line) and '000001' in line for line in sections.splitlines()):raise RuntimeError('ready NOBITS extent changed')
    placed=OUT/'tracepoint-file-list-ready-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(objects[1]),'-o',str(placed)],check=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_local_file_list_ready')!=0x20074ae4:raise RuntimeError('ready address changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-request-file-name-5ee1f8.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*(str(p) for p in objects),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=190 or len(after)!=192 or before-after!={'audio_tracepoint_request_file_name_5ee1f8'} or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REQUEST_FILE_NAME_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (FORMAT,SOURCE)],
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':64,
         'format_oracle':str(FORMAT_OUT.relative_to(ROOT)),'format_oracle_sha256':sha(FORMAT_OUT),'format_native_c_cases':64,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_address':'0x20074ae4','section_bytes':1,'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
         'object_sha256':[sha(p) for p in objects],
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':190,'unresolved_after':192,
         'imports_resolved':['audio_tracepoint_request_file_name_5ee1f8'],'imports_added':sorted(ADDED),
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Request and formatter compared at controlled child boundaries with logging disabled; reset, prepare and scan children exposed.','Ready flag is a bounded NOLOAD reservation; final RAM layout and startup remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
