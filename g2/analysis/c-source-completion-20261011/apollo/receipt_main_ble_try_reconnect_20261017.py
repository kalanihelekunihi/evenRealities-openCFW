#!/usr/bin/env python3
"""Bind stock-matched BLE reconnect policy into the current Main C candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-ble-try-reconnect'
PRIOR=BASE/'main-case-reconnect-state/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/ble_master_try_reconnect_4a316c_20261017.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'try-reconnect.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_BLE_TRY_RECONNECT_C'
    assert oracle['cases']==156 and oracle['source_sha256']==sha(SOURCE)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_box_reconnect_attempt_4a316c']
    assert added==['audio_ble_master_is_connected_4a22c6']
    assert len(prior)==99 and len(current)==99
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_BLE_TRY_RECONNECT_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'oracle':ref(ORACLE),
            'unresolved_before':99,'unresolved_after':99,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'BLE reconnect policy matches 156 bounded stock cases. Its lower connected predicate at 0x4a22c6 and final state/startup contracts remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
