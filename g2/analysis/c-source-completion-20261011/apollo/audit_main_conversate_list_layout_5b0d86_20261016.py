#!/usr/bin/env python3
"""Pin stock-compared Conversate list layout refresh in current Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-list-container-5b12ba/candidate.o';HERE=BASE/'main-conversate-list-layout-5b0d86'
CANDIDATE=HERE/'candidate.o';SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_main_list_layout_5b0d86.c';ORACLE=HERE/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 if len(before)!=130 or before!=after:raise RuntimeError('list layout frontier changed')
 row=json.loads(ORACLE.read_text())
 if row['status']!='PASS_DIRECT_MAIN_CONVERSATE_LIST_LAYOUT_5B0D86_C' or row['cases']!=48 or row['native_body']!='0x5b0d86..0x5b0edb' or row['source_sha256']!=sha(SOURCE) or row['source_complete'] or row['flashable'] or row['hardware_proof']:raise RuntimeError('list layout oracle changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 if ' audio_conversate_ui_main_list_layout_5b0d86\n' not in defined:raise RuntimeError('list layout body missing')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_LIST_LAYOUT_5B0D86_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'source':ref(SOURCE),'oracle_receipt':ref(ORACLE),'native_body':row['native_body'],'oracle_cases':row['cases'],'unresolved_before':130,'unresolved_after':130,'removed_imports':[],'new_imports':[],'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Display-main-page route 0x5b2d64, other Main imports and full-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
