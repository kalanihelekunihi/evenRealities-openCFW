#!/usr/bin/env python3
"""Pin stock-compared bounce callback chain in current Main candidate."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2';BASE=G2/'build/c-firmware/20261016'
PRIOR=BASE/'main-conversate-bounce-play-58a680/candidate.o'
HERE=BASE/'main-conversate-bounce-phase2-58a5a4';CANDIDATE=HERE/'candidate.o'
ORACLES=[BASE/'main-conversate-bounce-phase1-58a408/oracle-receipt.json',HERE/'oracle-receipt.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines() if line.strip()}
def main():
 before,after=imports(PRIOR),imports(CANDIDATE)
 removed={'audio_conversate_bounce_y_58a3fc','audio_conversate_bounce_phase1_done_58a408'}
 if len(before)!=133 or len(after)!=131 or before-after!=removed or after-before:
  raise RuntimeError('bounce callback frontier changed')
 rows=[json.loads(p.read_text()) for p in ORACLES]
 if [r['status'] for r in rows]!=['PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PHASE1_58A408_C','PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PHASE2_58A5A4_C'] or [r['cases'] for r in rows]!=[120,120] or any(r['source_complete'] or r['flashable'] or r['hardware_proof'] for r in rows):
  raise RuntimeError('bounce callback oracles changed')
 defined=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(CANDIDATE)],text=True)
 for name in ['audio_conversate_bounce_y_58a3fc','audio_conversate_bounce_phase1_done_58a408','audio_conversate_bounce_phase2_y_58a598','audio_conversate_bounce_phase2_done_58a5a4']:
  if f' {name}\n' not in defined:raise RuntimeError(f'missing {name}')
 record={'status':'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_CALLBACKS_INTEGRATION','prior_candidate':ref(PRIOR),'candidate_object':ref(CANDIDATE),'oracle_receipts':[ref(p) for p in ORACLES],'oracle_cases':240,'unresolved_before':133,'unresolved_after':131,'removed_imports':sorted(before-after),'new_imports':[],'source_complete':False,'flashable':False,'hardware_proof':False,'remaining_gate':'Final bounce RAM placement, other Main imports and full-image configuration remain open.'}
 path=HERE/'receipt.json';path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 print(record['status'],len(after),sha(path))
if __name__=='__main__':main()
