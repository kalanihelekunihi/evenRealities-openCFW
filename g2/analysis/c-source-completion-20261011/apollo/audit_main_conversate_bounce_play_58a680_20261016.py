#!/usr/bin/env python3
"""Pin stock-compared bounce play and stop in current Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
BASE = G2 / 'build/c-firmware/20261016'
PRIOR = BASE / 'main-conversate-main-scroll-down-5b2a64/candidate.o'
HERE = BASE / 'main-conversate-bounce-play-58a680'
CANDIDATE = HERE / 'candidate.o'
STOP_ORACLE = BASE / 'main-conversate-bounce-stop-58a7d2/oracle-receipt.json'
PLAY_ORACLE = HERE / 'oracle-receipt.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines() if line.strip()}
def main():
    before, after = imports(PRIOR), imports(CANDIDATE)
    removed = {'audio_conversate_main_list_scroll_58a680'}
    added = {'audio_conversate_bounce_y_58a3fc', 'audio_conversate_bounce_phase1_done_58a408'}
    if (len(before), len(after)) != (132, 133) or before-after != removed or after-before != added:
        raise RuntimeError('bounce play frontier changed')
    stop, play = json.loads(STOP_ORACLE.read_text()), json.loads(PLAY_ORACLE.read_text())
    if (stop['status'] != 'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_STOP_58A7D2_C' or
        stop['cases'] != 135 or play['status'] != 'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PLAY_58A680_C' or
        play['cases'] != 540 or stop['source_complete'] or play['source_complete'] or
        play['flashable'] or play['hardware_proof']):
        raise RuntimeError('bounce oracle changed')
    defined = subprocess.check_output(['arm-none-eabi-nm', '--defined-only', str(CANDIDATE)], text=True)
    if (' audio_conversate_main_list_scroll_58a680\n' not in defined or
        ' audio_conversate_bounce_stop_58a7d2\n' not in defined or
        ' audio_conversate_bounce_state_20073e14\n' not in defined):
        raise RuntimeError('bounce source or state missing')
    record = {'status': 'PASS_DIRECT_MAIN_CONVERSATE_BOUNCE_PLAY_58A680_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CANDIDATE),
              'stop_oracle_receipt': ref(STOP_ORACLE), 'play_oracle_receipt': ref(PLAY_ORACLE),
              'native_bodies': [stop['native_body'], play['native_body']],
              'oracle_cases': stop['cases'] + play['cases'],
              'unresolved_before': len(before), 'unresolved_after': len(after),
              'removed_imports': sorted(removed), 'new_imports': sorted(added),
              'source_complete': False, 'flashable': False, 'hardware_proof': False,
              'remaining_gate': 'Bounce callbacks, final state placement, other Main imports and image configuration remain open.'}
    receipt = HERE / 'receipt.json'
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(receipt))
if __name__ == '__main__': main()
