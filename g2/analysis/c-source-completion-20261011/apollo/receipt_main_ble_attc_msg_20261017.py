#!/usr/bin/env python3
"""Bind stock-matched Cordio ATT client message callback and pending Write Command helper."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-ble-attc-msg'
PRIOR=BASE/'main-ble-attc-send-mtu/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ble_attc_msg_5315b4_20261017.c'
PENDING=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ble_attc_pend_write_cmd_530d74_20261017.c'
ORACLE, PEND_ORACLE=HERE/'oracle-receipt.json',BASE/'main-ble-attc-pend-write-cmd/oracle-receipt.json'
OBJECT,PEND_OBJECT,CURRENT=HERE/'msg.o',HERE/'pend.o',HERE/'candidate.o'
OUT=HERE/'receipt.json'
UPSTREAM=ROOT/'third-party/upstream/cordio/ble-host/sources/stack/att/attc_main.c'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):return sorted({line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle,pending=json.loads(ORACLE.read_text()),json.loads(PEND_ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_BLE_ATTC_MSG_C' and oracle['cases']==80
    assert pending['status']=='PASS_BOUNDED_MAIN_BLE_ATTC_PEND_WRITE_CMD_C' and pending['cases']==75
    assert oracle['source_sha256']==sha(SOURCE) and pending['source_sha256']==sha(PENDING)
    upstream=UPSTREAM.read_text()
    assert 'void attcMsgCback' in upstream and 'bool_t attcPendWriteCmd' in upstream
    flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c']
    subprocess.run(flags+[str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(flags+[str(PENDING),'-o',str(PEND_OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),str(PEND_OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_ble_attc_msg_5315b4'] and added==[]
    assert len(prior)==102 and len(current)==101
    assert {'audio_ble_attc_msg_5315b4','audio_ble_attc_pend_write_cmd_530d74'}.issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_BLE_ATTC_MSG_C_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),'source':ref(SOURCE),'pending_source':ref(PENDING),'oracle':ref(ORACLE),'pending_oracle':ref(PEND_ORACLE),'dependency_source':ref(UPSTREAM),'unresolved_before':102,'unresolved_after':101,'removed_imports':removed,'new_imports':added,'new_providers':['audio_ble_attc_msg_5315b4','audio_ble_attc_pend_write_cmd_530d74'],'remaining_gate':'ATT client message callback and pending Write Command slot match bounded stock behavior; stock timeout dispatch differs from pinned upstream and other Main handlers remain open.','source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
