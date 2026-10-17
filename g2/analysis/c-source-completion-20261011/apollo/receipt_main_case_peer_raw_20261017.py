#!/usr/bin/env python3
"""Bind provisional stock Case peer bytes to the current Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-peer-raw'
PRIOR=BASE/'main-case-sync-response/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_peer_raw_20261017.c'
PARENT=BASE/'main-case-sync-response/receipt.json'
OBJECT,CURRENT,OUT=HERE/'peer-raw.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    assert json.loads(PARENT.read_text())['status']=='PASS_MAIN_CASE_SYNC_RESPONSE_C_INTEGRATION'
    HERE.mkdir(parents=True,exist_ok=True)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    sections=subprocess.check_output(['arm-none-eabi-objdump','-h',str(OBJECT)],text=True)
    assert '.g2_ram_20074188' in sections
    size=subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(OBJECT)],text=True)
    assert '00000004 D audio_uart_case_peer_raw_20074188' in size
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_peer_raw_20074188']
    assert added==[] and len(prior)==99 and len(current)==98
    record={'status':'PASS_MAIN_CASE_PEER_RAW_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'response_receipt':ref(PARENT),
            'unresolved_before':99,'unresolved_after':98,
            'removed_imports':removed,'new_imports':added,
            'observed_extent':4,
            'remaining_gate':'Four stock Case peer bytes have C storage. Final linker placement, adjacent cell layout and startup initialization remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
