#!/usr/bin/env python3
"""Bind sorted tracepoint inventory and bounded NOLOAD state to Main."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
BASE=G2/'build/c-firmware/20261015/main-file-lfs-dir-drop-4cc5a2/apollo-main-file-lfs-dir-drop-4cc5a2.o'
SOURCE=G2/'components/audio/uart_thread_source_candidate/tracepoint_insert_file_sorted_5edbb0.c'
STORAGE=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_inventory_2037cd24.c'
LINKER=G2/'components/audio/uart_thread_source_candidate/tracepoint_file_inventory_2037cd24.ld'
VERIFY=G2/'analysis/c-source-completion-20261011/apollo/verify_main_tracepoint_insert_file_sorted_5edbb0_20261015.py'
OUT=G2/'build/c-firmware/20261015/main-tracepoint-insert-file-sorted-5edbb0'
OWNED={'audio_tracepoint_insert_file_sorted_5edbb0','audio_tracepoint_file_inventory'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(*args):return subprocess.check_output(args,text=True)
def names(p,flag):return {line.split()[-1] for line in out('arm-none-eabi-nm','-g',flag,str(p)).splitlines() if line.strip()}
def main():
    subprocess.run([sys.executable,str(VERIFY)],check=True,capture_output=True,text=True)
    oracle_path=OUT/'oracle.json';oracle=json.loads(oracle_path.read_text())
    if oracle['status']!='PASS_BOUNDED_MAIN_TRACEPOINT_SORTED_INSERT_NATIVE_C' or oracle['native_c_cases']!=50 or oracle['source_sha256']!=sha(SOURCE) or oracle['storage_sha256']!=sha(STORAGE):raise RuntimeError('sorted-insert oracle changed')
    if '0x2037cd24 (NOLOAD)' not in LINKER.read_text():raise RuntimeError('inventory placement changed')
    OUT.mkdir(parents=True,exist_ok=True);objects=[]
    for path in (SOURCE,STORAGE):
        obj=OUT/(path.stem+'.o')
        subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(path),'-o',str(obj)],check=True)
        objects.append(obj)
    if set().union(*(names(p,'--defined-only') for p in objects))!=OWNED:raise RuntimeError('inventory symbols changed')
    sections=out('arm-none-eabi-readelf','-SW',str(objects[1]))
    if not any(re.search(r'\s\.bss\.opencfw\.tracepoint\.file_inventory\s+NOBITS\s+',line) and '000088' in line for line in sections.splitlines()):raise RuntimeError('inventory NOBITS extent changed')
    placed=OUT/'tracepoint-file-inventory-placement.o'
    subprocess.run(['arm-none-eabi-ld','-r','-T',str(LINKER),str(objects[1]),'-o',str(placed)],check=True)
    addresses={line.split()[-1]:int(line.split()[0],16) for line in out('arm-none-eabi-nm','-g','--defined-only',str(placed)).splitlines()}
    if addresses.get('audio_tracepoint_file_inventory')!=0x2037cd24:raise RuntimeError('inventory placement changed')
    before=names(BASE,'-u');linked=OUT/'apollo-main-tracepoint-insert-file-sorted-5edbb0.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(BASE),*(str(p) for p in objects),'-o',str(linked)],check=True)
    after=names(linked,'-u')
    if len(before)!=190 or after!=before:raise RuntimeError((len(before),len(after),before-after,after-before))
    row={'status':'PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SORTED_INSERT_C',
         'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),
         'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in (SOURCE,STORAGE)],
         'oracle':str(oracle_path.relative_to(ROOT)),'oracle_sha256':sha(oracle_path),'native_c_cases':50,
         'linker_fragment':str(LINKER.relative_to(ROOT)),'linker_sha256':sha(LINKER),
         'placement_object':str(placed.relative_to(ROOT)),'placement_sha256':sha(placed),
         'placement_address':'0x2037cd24','section_bytes':0x88,'section_type':'NOBITS',
         'base_object':str(BASE.relative_to(ROOT)),'base_sha256':sha(BASE),
         'object_sha256':[sha(p) for p in objects],
         'linked_object':str(linked.relative_to(ROOT)),'linked_sha256':sha(linked),
         'source_owned_symbols':sorted(OWNED),'unresolved_before':190,'unresolved_after':190,
         'imports_resolved':[],'imports_added':[],'source_complete':False,'full_payload_linked':False,'hardware_proof':False,
         'limits':['Sorted insertion was compared under logging-disabled controlled cases; RAM reservation final layout and startup remain open.']}
    path=OUT/'receipt.json';path.write_text(json.dumps(row,indent=2)+'\n')
    print(row['status'],len(before),len(after),sha(path))
if __name__=='__main__':main()
