#!/usr/bin/env python3
"""Integrate stock-matched Case force-out handler and expose lower frontier."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-force-out'
PRIOR=BASE/'main-case-sync-data/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_force_out_4ac5a2_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'force.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_FORCE_OUT_C'
    assert oracle['cases']==75 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_force_out_4ac5a2']
    assert added==['audio_uart_case_display_refresh_4abf86',
                   'audio_uart_case_force_out_apply_4ac798',
                   'audio_uart_case_force_out_finish_4ac19c',
                   'audio_uart_case_notify_4abec8']
    assert len(prior)==98 and len(current)==101
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_FORCE_OUT_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':98,'unresolved_after':101,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Case force-out flag handler matches 75 bounded stock cases and shares the existing 0x20075012 cell with Case status. Four lower product calls remain explicit imports; their source and hardware effects remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
