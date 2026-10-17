#!/usr/bin/env python3
"""Bind provisional Case nanopb product RAM with exact observed extents."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017';HERE=BASE/'main-case-status-send-storage'
HERE.mkdir(parents=True,exist_ok=True)
PRIOR=BASE/'main-case-status-send/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_status_send_storage_20261017.c'
SENDER=BASE/'main-case-status-send/receipt.json'
OBJECT,CURRENT,OUT=HERE/'storage.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    sender=json.loads(SENDER.read_text())
    assert sender['status']=='PASS_MAIN_CASE_STATUS_SEND_C_INTEGRATION'
    assert sender['candidate_object']['sha256']==sha(PRIOR)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    rows=[row.split() for row in subprocess.check_output(['arm-none-eabi-nm','-S',str(OBJECT)],text=True).splitlines()]
    sizes={row[-1]:int(row[1],16) for row in rows if len(row)==4}
    assert sizes['audio_uart_case_tx_frame_200f5a9c']==10
    assert sizes['audio_uart_case_tx_encoded_2037c5a0']==256
    assert sizes['audio_uart_case_tx_magic_20074ffa']==1
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_tx_encoded_2037c5a0',
                    'audio_uart_case_tx_frame_200f5a9c',
                    'audio_uart_case_tx_magic_20074ffa'] and added==[]
    assert len(prior)==103 and len(current)==100
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_STATUS_SEND_STORAGE_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'sender_receipt':ref(SENDER),
            'observed_extents':{'frame':10,'encoded':256,'magic':1},
            'unresolved_before':103,'unresolved_after':100,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'C backing matches observed minimum extents for Case nanopb frame/output/magic. Stock startup values, final RAM placement and descriptor 0x77793c remain unverified.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
