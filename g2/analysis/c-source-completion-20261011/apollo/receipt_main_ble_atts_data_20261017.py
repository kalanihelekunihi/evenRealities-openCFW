#!/usr/bin/env python3
"""Bind stock-matched Cordio ATT server data dispatcher with explicit child frontier."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-ble-atts-data'
PRIOR=BASE/'main-ble-attc-conn/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ble_atts_data_53498c_20261017.c'
ORACLE,OBJECT,CURRENT=HERE/'oracle-receipt.json',HERE/'data.o',HERE/'candidate.o'
OUT=HERE/'receipt.json'
UPSTREAM=ROOT/'third-party/upstream/cordio/ble-host/sources/stack/att/atts_main.c'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):return sorted({line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_BOUNDED_MAIN_BLE_ATTS_DATA_C'
    assert oracle['cases']==392 and oracle['source_sha256']==sha(SOURCE)
    upstream=UPSTREAM.read_text()
    assert 'static void attsDataCback' in upstream and 'const uint8_t attsMinPduLen[]' in upstream
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    children=['audio_ble_atts_ccb_by_handle_5351a8','audio_ble_atts_csf_act_client_state_52caa8','audio_ble_atts_proc_table_2000045c']
    assert removed==['audio_ble_atts_data_53498c'] and added==children
    assert len(prior)==100 and len(current)==102
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_BLE_ATTS_DATA_C_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),'source':ref(SOURCE),'oracle':ref(ORACLE),'dependency_source':ref(UPSTREAM),'unresolved_before':100,'unresolved_after':102,'removed_imports':removed,'new_imports':added,'new_providers':removed,'remaining_gate':'ATT server data dispatcher matches bounded stock opcode, length, client-state and error paths; server CCB lookup, CSF state gate and source-owned process table are now explicit child gates.','source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
