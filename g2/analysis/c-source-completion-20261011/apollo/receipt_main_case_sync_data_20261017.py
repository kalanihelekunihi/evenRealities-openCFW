#!/usr/bin/env python3
"""Integrate stock-matched Case sync data handler and expose its lower frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-sync-data'
PRIOR=BASE/'main-uart-sync-storage/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_sync_data_4acb40_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'case.o',HERE/'candidate.o',HERE/'receipt.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})

def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_SYNC_DATA_C'
    assert oracle['cases']==85 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_registry_callback_4acb40']
    assert added==['audio_uart_case_force_out_4ac5a2',
                   'audio_uart_case_sync_event_510a0c',
                   'audio_uart_case_sync_response_4ac890']
    assert len(prior)==96 and len(current)==98
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_SYNC_DATA_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':96,'unresolved_after':98,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Case sync data handler matches 85 bounded stock cases. Three lower product handlers are now explicit imports; their behavior, broader packet coverage and physical Case transport remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))

if __name__=='__main__':main()
