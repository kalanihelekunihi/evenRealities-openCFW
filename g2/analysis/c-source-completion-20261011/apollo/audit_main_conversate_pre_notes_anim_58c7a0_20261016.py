#!/usr/bin/env python3
"""Pin stock-compared prep-notes anim and its unresolved six-frame RAM array."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-display-style-5b22bc/candidate.o';HERE=BASE/'main-conversate-pre-notes-anim-58c7a0'
CANDIDATE=HERE/'candidate.o';SOURCE=G2/'components/audio/uart_thread_source_candidate/conversate_pre_notes_anim_58c7a0.c';ORACLE=HERE/'oracle-receipt.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 added={'audio_conversate_anim_frames_20000bf4'}
 if len(before)!=130 or len(after)!=131 or before-after or after-before!=added:raise RuntimeError('pre-notes anim frontier changed')
 row=json.loads(ORACLE.read_text())
 if row['status']!='PASS_DIRECT_MAIN_CONVERSATE_PRE_NOTES_ANIM_58C7A0_C' or row['cases']!=16 or row['native_bodies']!=['0x58c7a0..0x58c823','0x58c824..0x58c835'] or row['source_sha256']!=sha(SOURCE) or row['source_complete'] or row['flashable'] or row['hardware_proof']:raise RuntimeError('pre-notes anim oracle changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 for name in ('audio_conversate_pre_notes_anim_create_58c7a0','audio_conversate_pre_notes_anim_start_58c824'):
  if f' {name}\n' not in defined:raise RuntimeError(f'missing {name}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_PRE_NOTES_ANIM_58C7A0_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'source':ref(SOURCE),'oracle_receipt':ref(ORACLE),'native_bodies':row['native_bodies'],'oracle_cases':row['cases'],'unresolved_before':130,'unresolved_after':131,'removed_imports':[],'new_imports':sorted(added),'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Native RAM 0x20000bf4 six-frame pointer array source ownership, display-main-page route 0x5b2d64, other Main imports and full-image gates remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
