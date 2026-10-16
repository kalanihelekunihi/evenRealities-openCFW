#!/usr/bin/env python3
"""Audit source scanf conversions and the controlled emulator-observation repair."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scanf-conversion';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();bp=BASE/'native-scanf-conversion-runtime/report.json';bundle=read(bp)
 assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert r['counts']=={'integer':9800,'string':3312,'getc':6144,'ungetc':6144} and r['comparisons']==25400 and r['callback_comparisons']==80373 and r['trace_sha256']=='656e04a0900151c919acce8c3539303b3a085ef32107bd4ff2278cea4ee0d76e'
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_scanf_conversion.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_scanf_conversion.o')==report['units'][0]['object_sha256']
 assert r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-scanf-conversion-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
 assert r['analysis_elf_sha256']==sha(ROOT/'r1/research/source-build/i2c5/stock-analysis-exec.elf')=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
 assert r['layout_sha256']==sha(ROOT/r['layout']) and not report['application_linked'] and not report['instruction_identity'] and not r['instruction_identity']
 for flag in ['return_stack_callee_integer_full_arena_and_nonstack_write_order_checked','callback_transcripts_checked','executed_store_observer_with_full_arena_reconciliation','unicorn_memory_write_hooks_disabled','whitespace_callback_fixture','source_input_callbacks_and_digit','signed_unsigned_byte_short_word_and_suppression','integer_radix_and_prefix_boundaries','string_character_and_scanset_modes','all_input_byte_values','runtime_no_unresolved']:assert r[flag]
 assert r['whitespace_fixture_sha256']==sha(ROOT/r['whitespace_fixture_source'])
 for data in [report,bundle]:
  for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x278d0,332),(0x27a1c,224),(0x28038,30),(0x28056,34)]:
  assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
  evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'))
  assert evidence['error']['code']=='invalid_request' and 'No procedure exists' in str(evidence)
 assert e['native_body_bytes']==620 and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')
 it=read(OUT/'it-memory-hook-reproduction.json');assert it['unicorn_version']=='2.1.4' and it['verification_only'] and it['driver_sha256']==sha(ROOT/'r1/tools/verify_unicorn_it_memory_hook.py') and it['fixture_sha256']==sha(ROOT/it['fixture']) and it['layout_sha256']==sha(ROOT/it['layout'])
 assert it['results'][0]['pc']==0x20000100 and it['results'][0]['sp']==0x2003f000 and it['results'][0]['error'] is None and it['results'][1]['pc']!=0x20000100 and it['results'][1]['error']
 assert e['initial_return_counterexample_sha256']==sha(OUT/'initial-return-counterexample.log') and e['emulator_reproduction_sha256']==sha(OUT/'it-memory-hook-reproduction.json')
 review=read(OUT/'memory-hook-review-gate.json');assert review['status']=='pending-conditional-thumb-store-exposure-review' and not review['external_blocker'] and review['direct_named_memory_hook_driver_count']==len(review['drivers'])==88
 for p,h in {**review['drivers'],**review['controlled_replay_driver']}.items():assert sha(ROOT/p)==h,p
 print('Native scanf conversions authenticated: 25400 cases; store observer reconciled with full arena; full parser/ABI/image gates remain open')
if __name__=='__main__':audit()
