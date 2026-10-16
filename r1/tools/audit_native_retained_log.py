#!/usr/bin/env python3
"""Authenticate the bounded retained sink and explicit downstream gate."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-retained-log';r=json.loads((out/'verification.json').read_text());b=json.loads((BASE/'native-retained-log-runtime/report.json').read_text())
 assert r['comparisons']==2016 and r['observation_counts']==dict(clear=672,initialize=336,format=636,output=424) and r['trace_sha256']=='2a30ec25e111a39e79a50f3d0b2feaa351f9ad676a55b697831cdd2fba866de0'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'native_retained_log.o')==r['object_sha256'] and sha(ROOT/'r1/tools/verify_native_retained_log.py')==r['driver_sha256'] and sha(BASE/'native-retained-log-rea.json')==r['rea_sha256'] and sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')==r['application_sha256']
 for flag in ['actual_sink_body','callees_are_fixtures','external_frame32_and_varargs_pointer_checked','raw_r0_callee_sp_context_output_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','composed_formatter_rtt_crash_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=BASE/'native-retained-log-runtime/native-retained-log-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==24
 assert b['closed_parent_imports']==['r1_retained_log_printf_sink'] and b['newly_exposed_imports']==['r1_health_crash_record_initializer'] and b['canonical_reset_context_reused']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Retained log:2016 bounded cases; crash initializer gate explicit')
if __name__=='__main__':audit()
