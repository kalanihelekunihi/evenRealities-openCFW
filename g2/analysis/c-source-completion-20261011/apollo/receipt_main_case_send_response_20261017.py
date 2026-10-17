#!/usr/bin/env python3
"""Bind stock-matched Case response encoder and local getters to Main."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-send-response'
PRIOR=BASE/'main-case-rx-info/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_send_response_510c70_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'send-response.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_CASE_SEND_RESPONSE_C'
    assert oracle['cases']==360 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_send_response_510c70']
    assert added==[] and len(prior)==97 and len(current)==96
    owned=['audio_uart_case_send_response_510c70','audio_uart_case_local_soc_4ac726',
           'audio_uart_case_local_charge_4ac73c','audio_uart_case_local_lid_4ac752']
    assert set(owned).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_SEND_RESPONSE_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':97,'unresolved_after':96,
            'removed_imports':removed,'new_imports':added,'owned_symbols':owned,
            'remaining_gate':'Case response encoder and three local status getters match 360 bounded stock cases. Whole-image RAM placement, startup and BLE transport remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
