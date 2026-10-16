#!/usr/bin/env python3
"""Bind tracepoint pull reset and observed connection flag to Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_reset_pull_478110.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_connection_flag_20074f8f.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_reset_pull_478110_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-reset-pull-478110'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-prepare-pull-48ec9e/apollo-main-tracepoint-prepare-pull-48ec9e.o'
OWNED={'audio_tracepoint_reset_pull_478110','audio_tracepoint_pull_connection_flag_20074f8f'}
EXPECTED={'audio_ble_current_conn_mode','audio_ble_connect_param_request','audio_event_loop_remove_delayed','audio_event_loop_push_delayed'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*args):return subprocess.check_output(args,text=True)
def names(p,flag):return {line.split()[-1] for line in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_RESET_PULL_NATIVE_C' or oracle['native_c_cases']!=12 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('reset oracle changed')
    if '0x20074f8f (NOLOAD)' not in LINKER.read_text():raise RuntimeError('reset flag placement changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_reset_pull_478110.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!=EXPECTED:raise RuntimeError('reset source contract changed')
    sections=out('arm-none-eabi-readelf','-SW',str(obj))
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.pull_connection_flag\s+NOBITS\s+',line) and '000001' in line for line in sections.splitlines()):raise RuntimeError('reset flag NOBITS extent changed')
    placed=OUT/'tracepoint-pull-connection-flag-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_pull_connection_flag_20074f8f')!=0x20074f8f:raise RuntimeError('reset flag address changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-reset-pull-478110.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=195 or len(after)!=194 or before-after!={'audio_tracepoint_reset_pull_478110'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_RESET_PULL_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':12,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_address':'0x20074f8f','section_bytes':1,'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':195,'unresolved_after':194,
         'imports_resolved':['audio_tracepoint_reset_pull_478110'],'imports_added':[],
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Reset passed 12 controlled native/C event-loop cases; 1-byte flag reservation final layout and startup remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
