#!/usr/bin/env python3
"""Audit source scanf core/frontend closure without promoting raw ABI/image gates."""
import contextlib,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scanf-core';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_ctype import audit as history
 with contextlib.redirect_stdout(io.StringIO()):history()
 r=read(OUT/'verification.json');direct=read(OUT/'entry-verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();bp=BASE/'native-sscanf-runtime/report.json';bundle=read(bp)
 assert r['comparisons']==38356 and r['counts']=={'grid':36374,'compound':450,'byte_prefix':1020,'random':512} and r['callback_comparisons']==490402 and r['trace_sha256']=='cdacaee5a04bfc90e45fa714ab82d4976348825b506bf7daf605f160996a0596'
 assert direct['comparisons']==572 and direct['counts']=={'core':286,'descriptor':286} and direct['callback_comparisons']==6658 and direct['trace_sha256']=='2b4090f9f93bcd134359b7c11ac2066f7c0d43e03160f7f6d7be175361f1c723'
 assert r['entries']['compiled']['sscanf']==r['entries']['compiled']['core']==38356 and r['entries']['compiled']['descriptor']==0
 assert direct['entries']['compiled']==direct['entries']['native'] and direct['entries']['compiled']['descriptor']==286 and direct['entries']['compiled']['core']==572
 assert r['variadic_register_and_stack_outputs'] and r['source_frontend_core_conversions_ctype_and_input'] and not direct['variadic_register_and_stack_outputs'] and not direct['source_frontend_core_conversions_ctype_and_input'] and direct['source_core_descriptor_conversions_ctype_and_input'] and direct['callback_function_pointer_relocations_normalized']
 for receipt,driver in [(r,'verify_native_sscanf.py'),(direct,'verify_native_scanf_entries.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a' and receipt['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
  assert receipt['report_sha256']==sha(rp) and receipt['object_sha256']==sha(OUT/'native_scanf_core.o')==report['units'][0]['object_sha256'] and receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-sscanf-runtime.o')==bundle['linked_sha256']
  assert receipt['layout_sha256']==sha(ROOT/receipt['layout']) and not receipt['instruction_identity'] and not receipt['native_core_fixture']
  for flag in ['return_stack_callee_integer_full_arena_and_nonstack_write_order_checked','normalized_callback_transcripts_checked','runtime_no_unresolved','candidate_native_code_execution_forbidden','suppression_width_length_count_and_scanset_cases','native_float_and_long_long_nop_failures_preserved','executed_store_observer_with_full_arena_reconciliation','unicorn_memory_write_hooks_disabled']:assert receipt[flag]
 assert not bundle['undefined_symbols'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for data in [report,bundle]:
  for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-scanf-core/report.json','native-sscanf-frontend-runtime/report.json']}
 for p,h in e['ghidra'].items():assert sha(OUT/p)==h,p
 for a,n in [(0x283c4,810),(0x286f0,4),(0x28570,16),(0x285fe,12)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 assert e['rea_sha256']==sha(OUT/'rea-283c4.json');rea=read(OUT/'rea-283c4.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea)
 assert e['native_core_bytes']==810 and e['native_frontend_bytes']==48 and e['native_descriptor_initializer_bytes']==20 and e['core_numeric_bytes']==4 and e['core_frame_bytes']==88 and e['source_descriptor_mode_zero'] and e['alternate_descriptor_private_frame_gate'] and not e['locked_ownership_changed']
 assert e['prior_frontend_evidence_sha256']==sha(BASE/'native-sscanf-frontend/evidence.json') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')
 from audit_source_frontier import section_bytes
 assert section_bytes(OUT/'native_scanf_core.o','.r1.scanf.width_limit',executable=False)==raw[0x286f0-0x27000:0x286f4-0x27000]
 assert raw[0x2857a-0x27000:0x2857e-0x27000]==raw[0x28604-0x27000:0x28608-0x27000]==bytes.fromhex('aff30080')
 print('Source scanf frontend/core authenticated: 38356 variadic plus572 direct entry calls; no native core fixture; raw ABI/startup/image gates remain open')
if __name__=='__main__':audit()
