#!/usr/bin/env python3
"""Audit native signed/wrapping GPIO command behavior without target admission."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-output-gpio-command-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==11232 and r['counts']==dict(reject=2592,missing=1080,unopened=2520,direct=1680,delayed=3360) and r['observation_counts']==dict(compare=30960,driver=5040,delay=3360) and r['trace_sha256']=='3790e3b765016f172404c4e79de5fbc4f263cbbf0eb27a33ccec5570d909a0e1'
 for flag in ['actual_strcmp','only_driver_delay_are_fixtures','mapped_negative_and_wrapping_indices_checked','fresh_name_and_callback_mutations_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['arbitrary_negative_targets_verified','full_raw_abi_verified','cross_call_private_frame_history_verified','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_output_gpio_command.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'output-command-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_output_gpio_command_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-output-gpio-command-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-output-gpio-command-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==44
 assert undefined_symbols(out/'output-command-source.o')[0]==b['graph_undefined_symbols']==['r1_output_gpio_close','r1_output_gpio_open']
 assert b['closed_parent_imports']==['r1_output_gpio_slot18'] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 q=json.loads((BASE/'native-output-gpio-command/rea-bytes-54d20.json').read_text())['structuredContent'];d=q['normalized_result'];i=0x54d20-0x27000
 assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==108 and bytes.fromhex(d['bytes_hex'])==raw[i:i+108]
 print('GPIO command:11232 cases;actual strcmp;negative/wrapping table indices;44 imports;arbitrary-target/ABI/image gates open')
if __name__=='__main__':audit()
