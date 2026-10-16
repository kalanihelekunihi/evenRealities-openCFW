#!/usr/bin/env python3
"""Authenticate selected existing providers without claiming new runtime proof."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-printf-runtime';r=json.loads((out/'report.json').read_text())
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports','existing_verification_receipts']:
  for p,h in r[group].items():assert sha(BASE/p)==h,p
 selected=out/'printf-source.o';linked=out/'native-printf-runtime.o'
 assert sha(selected)==r['selected_sha256'] and sha(linked)==r['linked_sha256']
 assert undefined_symbols(selected)==(r['selected_undefined_symbols'],r['selected_defined_symbols'])
 assert undefined_symbols(linked)[0]==r['undefined_symbols'] and len(r['undefined_symbols'])==24
 assert r['closed_parent_imports']==['printf'] and r['newly_exposed_imports']==[] and r['existing_formatter_and_rtt_state_reused']
 for flag in ['new_source_bodies','composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Existing printf composition authenticated:24 unresolved imports')
if __name__=='__main__':audit()
