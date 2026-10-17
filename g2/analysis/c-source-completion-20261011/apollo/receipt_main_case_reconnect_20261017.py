#!/usr/bin/env python3
"""Integrate bounded Case reconnect provider into the current Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-reconnect'
PRIOR=BASE/'main-case-descriptor/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_reconnect_4ac19c_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'reconnect.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_RECONNECT_C'
    assert oracle['cases']==400 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_force_out_finish_4ac19c']
    assert added==['audio_box_reconnect_pending_20075011','audio_box_reconnect_suppressed_20075010',
                   'audio_uart_box_reconnect_attempt_4a316c']
    assert len(prior)==99 and len(current)==101
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_RECONNECT_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':99,'unresolved_after':101,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Case reconnect matches 400 bounded stock cases. The lower reconnect attempt at 0x4a316c and source ownership for two RAM state bytes remain unresolved.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
