#!/usr/bin/env python3
"""Bind the bounded stock Main pull-readiness routine to the C overlay."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_ready_48eb90.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_pull_ready_48eb90.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_pull_ready_48eb90_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-pull-ready-48eb90'
BASE=G2/'build/c-firmware/20261015/main-tracepoint-pull-initialize-47e1ec/apollo-main-tracepoint-pull-initialize-47e1ec.o'
OWNED={'audio_tracepoint_pull_ready_48eb90','audio_tracepoint_pull_backend_ready_20075035','audio_tracepoint_pull_failure_count_20074ac0'}
ADDED={'audio_tracepoint_pull_backend_init_47dfec','audio_tracepoint_pull_write_batch_47e178','audio_tracepoint_pull_complete_47e220'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*a):return subprocess.check_output(a,text=True)
def names(p,flag):return {s.split()[-1] for s in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if s.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_PULL_READY_NATIVE_C' or oracle['native_c_cases']!=256 or oracle['source_sha256']!=sha(SOURCE):raise RuntimeError('pull ready oracle changed')
    script=LINKER.read_text()
    if '0x20074ac0 (NOLOAD)' not in script or '0x20075035 (NOLOAD)' not in script:raise RuntimeError('pull ready placement changed')
    OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'tracepoint_pull_ready_48eb90.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    if names(obj,'--defined-only')!=OWNED or names(obj,'-u')-names(BASE,'--defined-only')!=ADDED:raise RuntimeError('pull ready source contract changed')
    sections=out('arm-none-eabi-readelf','-SW',str(obj))
    for section,size in [('pull_failure_count','000004'),('pull_backend_ready','000001')]:
        if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.'+section+r'\s+NOBITS\s+',line) and size in line for line in sections.splitlines()):raise RuntimeError(section+' NOBITS extent changed')
    placed=OUT/'tracepoint-pull-ready-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(obj),'-o',str(placed)],check=True)
    addresses={s.split()[-1]:int(s.split()[0],16) for s in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_pull_failure_count_20074ac0')!=0x20074ac0 or addresses.get('audio_tracepoint_pull_backend_ready_20075035')!=0x20075035:raise RuntimeError('pull ready address changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-pull-ready-48eb90.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),str(obj),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=190 or len(after)!=192 or before-after!={'audio_tracepoint_pull_ready_48eb90'} or after-before!=ADDED:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_READY_C','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':256,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_addresses':{'failure_count':'0x20074ac0','backend_ready':'0x20075035'},
         'section_bytes':{'failure_count':4,'backend_ready':1},'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),'object_sha256':sha(obj),
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':190,'unresolved_after':192,
         'imports_resolved':['audio_tracepoint_pull_ready_48eb90'],'imports_added':sorted(ADDED),
         'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Pull readiness passed 256 controlled native/C cases; backend children, final RAM layout/startup and hardware remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
