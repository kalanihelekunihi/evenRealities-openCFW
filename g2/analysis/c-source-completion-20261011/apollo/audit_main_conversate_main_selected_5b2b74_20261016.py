#!/usr/bin/env python3
"""Pin stock-compared Conversate main-page selection route."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-bounce-phase2-58a5a4/candidate.o'
HERE=BASE/'main-conversate-main-selected-5b2b74';CANDIDATE=HERE/'candidate.o'
SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_main_selected_5b2b74.c'
ORACLE=HERE/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 removed={'audio_conversate_ui_route_5b2b74'}
 if len(before)!=131 or len(after)!=130 or before-after!=removed or after-before:raise RuntimeError('selection frontier changed')
 row=json.loads(ORACLE.read_text())
 if row['status']!='PASS_DIRECT_MAIN_CONVERSATE_MAIN_SELECTED_5B2B74_C' or row['cases']!=80 or row['native_body']!='0x5b2b74..0x5b2c67' or row['source_sha256']!=sha(SOURCE) or row['source_complete'] or row['flashable'] or row['hardware_proof']:raise RuntimeError('selection oracle changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 if ' audio_conversate_ui_route_5b2b74\n' not in defined:raise RuntimeError('selection body missing')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_MAIN_SELECTED_5B2B74_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'source':ref(SOURCE),'oracle_receipt':ref(ORACLE),'native_body':row['native_body'],'oracle_cases':row['cases'],'unresolved_before':131,'unresolved_after':130,'removed_imports':sorted(removed),'new_imports':[],'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Other Main imports, final configuration and whole-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
