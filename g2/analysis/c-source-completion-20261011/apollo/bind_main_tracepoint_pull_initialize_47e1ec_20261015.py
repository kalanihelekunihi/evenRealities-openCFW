#!/usr/bin/env python3
"""Bind pull initialization and bounded pending/enable state to Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_initialize_47e1ec.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_initialize_47e1ec.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_pull_initialize_47e1ec_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-initialize-47e1ec'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-dir-facade-474b02/apollo-main-tracepoint-dir-facade-474b02.o'
OWNED={'audio_tracepoint_pull_initialize_47e1ec','audio_tracepoint_pull_pending_20074ad8','audio_tracepoint_pull_enabled_20075038'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*args):return subprocess.check_output(args,text=True)
def names(p,flag):return {line.split()[-1] for line in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_PULL_INITIALIZE_NATIVE_C' or oracle['native_c_cases']!=36 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('pull init oracle changed')
    script=LINKER.read_text()
    if '0x20074ad8 (NOLOAD)' not in script or '0x20075038 (NOLOAD)' not in script:raise RuntimeError('pull init placement changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_pull_initialize_47e1ec.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')!={'audio_tracepoint_close_active_file_47e06a'}:raise RuntimeError('pull init source contract changed')
    sections=out('arm-none-eabi-readelf','-SW',str(obj))
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.pull_pending\s+NOBITS\s+',line) and '000008' in line for line in sections.splitlines()):raise RuntimeError('pending NOBITS extent changed')
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.pull_enabled\s+NOBITS\s+',line) and '000001' in line for line in sections.splitlines()):raise RuntimeError('enabled NOBITS extent changed')
    placed=OUT/'tracepoint-pull-initialize-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_pull_pending_20074ad8')!=0x20074ad8 or addresses.get('audio_tracepoint_pull_enabled_20075038')!=0x20075038:raise RuntimeError('pull init address changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-pull-initialize-47e1ec.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=191 or len(after)!=190 or before-after!={'audio_tracepoint_pull_initialize_47e1ec'} or after-before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_INITIALIZE_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':36,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_addresses':{'pending':'0x20074ad8','enabled':'0x20075038'},
         'section_bytes':{'pending':8,'enabled':1},'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':191,'unresolved_after':190,
         'imports_resolved':['audio_tracepoint_pull_initialize_47e1ec'],'imports_added':[],
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Pull initialization passed 36 controlled native/C cases; final RAM layout/startup and hardware remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
