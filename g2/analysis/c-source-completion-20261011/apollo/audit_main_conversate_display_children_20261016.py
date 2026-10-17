#!/usr/bin/env python3
"""Pin display animation completion and LVGL label rule in Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-display-main-page-5b2d64/candidate.o';HERE=BASE/'main-lv-label-rule-43f6ac'
CANDIDATE=HERE/'candidate.o'
ORACLES=[BASE/'main-conversate-display-tick-5b22ee/oracle-receipt.json',HERE/'oracle-receipt.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 removed={'audio_conversate_display_tick_5b22ee','audio_uart_page_43f6ac'}
 if len(before)!=134 or len(after)!=132 or before-after!=removed or after-before:raise RuntimeError('display child frontier changed')
 rows=[json.loads(p.read_text()) for p in ORACLES]
 if [r['status'] for r in rows]!=['PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_TICK_5B22EE_C','PASS_DIRECT_MAIN_LV_LABEL_RULE_43F6AC_C'] or [r['cases'] for r in rows]!=[6,10] or any(r['source_complete'] or r['flashable'] or r['hardware_proof'] for r in rows):raise RuntimeError('display child oracles changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 for name in removed:
  if f' {name}\n' not in defined:raise RuntimeError(f'missing {name}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_DISPLAY_CHILDREN_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'oracle_receipts':[ref(p) for p in ORACLES],'oracle_cases':16,'unresolved_before':134,'unresolved_after':132,'removed_imports':sorted(removed),'new_imports':[],'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Title/icon data source, six-frame RAM array, other Main imports and whole-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
