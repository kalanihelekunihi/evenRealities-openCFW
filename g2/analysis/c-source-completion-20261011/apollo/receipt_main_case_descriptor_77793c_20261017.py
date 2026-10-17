#!/usr/bin/env python3
"""Integrate authenticated two-node Case nanopb C descriptor graph."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017';HERE=BASE/'main-case-descriptor'
PRIOR=BASE/'main-case-status-send-storage/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_descriptor_77793c_20261017.c'
MAP=HERE/'descriptor-map.json';ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'descriptor.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text());mapping=json.loads(MAP.read_text())
    assert oracle['status']=='PASS_MAIN_CASE_DESCRIPTOR_C_GRAPH'
    assert oracle['descriptors']==2 and oracle['source']['sha256']==sha(SOURCE)
    assert oracle['object']['sha256']==sha(OBJECT)
    assert mapping['source']['sha256']==sha(SOURCE)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_descriptor_77793c'] and added==[]
    assert len(prior)==100 and len(current)==99
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_DESCRIPTOR_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'extraction_map':ref(MAP),'oracle':ref(ORACLE),
            'unresolved_before':100,'unresolved_after':99,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Two-node Case nanopb descriptor graph matches authenticated stock field words and pointers. Final ROM layout, full encode behavior and physical delivery remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
