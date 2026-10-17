#!/usr/bin/env python3
"""Bind provisional Case reconnect RAM cells to the Main C candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-reconnect-state'
PRIOR=BASE/'main-case-reconnect/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_reconnect_state_20261017.c'
PARENT=BASE/'main-case-reconnect/receipt.json'
OBJECT,CURRENT,OUT=HERE/'state.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    assert json.loads(PARENT.read_text())['status']=='PASS_MAIN_CASE_RECONNECT_C_INTEGRATION'
    HERE.mkdir(parents=True,exist_ok=True)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    sections=subprocess.check_output(['arm-none-eabi-objdump','-h',str(OBJECT)],text=True)
    assert '.g2_ram_20075010' in sections and '.g2_ram_20075011' in sections
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_box_reconnect_pending_20075011','audio_box_reconnect_suppressed_20075010']
    assert added==[] and len(prior)==101 and len(current)==99
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_RECONNECT_STATE_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'reconnect_receipt':ref(PARENT),
            'unresolved_before':101,'unresolved_after':99,
            'removed_imports':removed,'new_imports':added,
            'stock_cells':{'suppressed':'0x20075010','pending':'0x20075011'},
            'remaining_gate':'Two one-byte stock Case reconnect cells have C storage; final linker placement, startup initialization and external mutations remain unresolved.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
