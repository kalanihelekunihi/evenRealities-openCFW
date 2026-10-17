#!/usr/bin/env python3
"""Pin stock-matched Conversate title/icon C data in Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-lv-label-rule-43f6ac/candidate.o';HERE=BASE/'main-conversate-prep-icon-76a47c'
CANDIDATE=HERE/'candidate.o';SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_prep_icon_76a47c.c';ORACLE=HERE/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 removed={'audio_conversate_prep_icon_76a47c','audio_conversate_title_label_5b3334'}
 if len(before)!=132 or len(after)!=130 or before-after!=removed or after-before:raise RuntimeError('prep icon frontier changed')
 row=json.loads(ORACLE.read_text())
 if row['status']!='PASS_MAIN_CONVERSATE_PREP_ICON_SOURCE_DATA' or row['native_icon']!='0x76a47c..0x76a497' or row['native_pixels']!='0x6aca80..0x6accbf' or row['native_title']!='0x5b3334..0x5b3337' or row['source_sha256']!=sha(SOURCE) or row['object_sha256']!=sha(ROOT/row['object']) or row['source_complete'] or row['flashable'] or row['hardware_proof']:raise RuntimeError('prep icon source data changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 for name in removed|{'audio_conversate_prep_icon_pixels_6aca80'}:
  if f' {name}\n' not in defined:raise RuntimeError(f'missing {name}')
 record={'status':'PASS_MAIN_CONVERSATE_PREP_ICON_SOURCE_DATA_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'source':ref(SOURCE),'oracle_receipt':ref(ORACLE),'unresolved_before':132,'unresolved_after':130,'removed_imports':sorted(removed),'new_imports':[],'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Six-frame RAM pointer array 0x20000bf4, other Main imports, final placement and whole-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
