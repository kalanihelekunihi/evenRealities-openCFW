#!/usr/bin/env python3
"""Integrate stock-matched Case status getters and their observed RAM cells."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017';HERE=BASE/'main-case-status-getters'
PRIOR=BASE/'main-case-notify/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_status_getters_20261017.c'
ORACLE=HERE/'oracle-receipt.json';OBJECT,CURRENT,OUT=HERE/'getters.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_STATUS_GETTERS_C'
    assert oracle['cases']==81 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_charge_4acaac','audio_uart_case_lid_4acab4',
                    'audio_uart_case_soc_4acaa0'] and added==[]
    assert len(prior)==103 and len(current)==100
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_STATUS_GETTERS_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':103,'unresolved_after':100,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Three Case status getters match 81 bounded stock cases. SOC and charge C cells are provisional source-owned RAM at 0x2007418c/8d; stock startup values and final placement remain open. Lid getter shares existing 0x2007418e cell.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
