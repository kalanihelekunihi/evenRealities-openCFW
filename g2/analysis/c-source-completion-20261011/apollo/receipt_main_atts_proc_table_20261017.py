#!/usr/bin/env python3
"""Bind vendor-attributable Cordio ATTS procedure table into Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-atts-proc-table'
PRIOR=BASE/'main-case-nonce-state/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ble_atts_proc_table_2000045c_20261017.c'
VENDOR=ROOT/'third-party/upstream/cordio/ble-host/sources/stack/att/atts_main.c'
ORACLE=HERE/'oracle-receipt.json'
OBJECT,CURRENT,OUT=HERE/'proc-table.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    oracle=json.loads(ORACLE.read_text())
    assert oracle['status']=='PASS_MAIN_ATTS_PROC_TABLE_SOURCE_MATCH'
    assert oracle['entries']==18 and oracle['unique_provider_symbols']==13
    assert oracle['source_sha256']==sha(SOURCE) and oracle['vendor_sha256']==sha(VENDOR)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    expected=sorted(set(x for x in oracle['provider_order'] if x))
    assert removed==['audio_ble_atts_proc_table_2000045c']
    assert added==expected and len(prior)==95 and len(current)==107
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_ATTS_PROC_TABLE_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'vendor_source':ref(VENDOR),'oracle':ref(ORACLE),
            'unresolved_before':95,'unresolved_after':107,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Cordio ATTS table row order and stock initialized words are source-backed. Thirteen handler bodies are now explicit imports; whole-image relocation/startup remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()
