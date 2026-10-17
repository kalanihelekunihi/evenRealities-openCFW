#!/usr/bin/env python3
"""Bind stock-matched Case nanopb RX dispatch into current Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-sync-event'
PRIOR=BASE/'main-case-in-case/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_sync_event_510a0c_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'sync-event.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_SYNC_EVENT_C'
    assert oracle['cases']==1008 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_sync_event_510a0c']
    assert added==['audio_uart_case_rx_frame_200f5a90','audio_uart_case_rx_info_510bfe',
                   'audio_uart_case_send_response_510c70']
    assert len(prior)==97 and len(current)==99
    record={'status':'PASS_MAIN_CASE_SYNC_EVENT_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':97,'unresolved_after':99,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Case nanopb RX dispatch matches 1008 bounded stock cases. Decoded info handler, response encoder, and 10-byte RX frame storage remain at this stage.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
