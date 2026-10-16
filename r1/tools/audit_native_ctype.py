#!/usr/bin/env python3
"""Audit native raw ctype data and closure of the scanf whitespace fixture."""
import contextlib,csv,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-ctype';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_scanf_conversion import audit as history
 with contextlib.redirect_stdout(io.StringIO()):history()
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();g=read(BASE/'native-scanf-conversion/source-whitespace-verification.json');bp=BASE/'native-scanf-runtime/report.json';bundle=read(bp)
 assert sha(app)==r['application_sha256']==g['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert r['counts']=={'pointer':4,'space':257} and r['comparisons']==261 and r['trace_sha256']=='94045e692c6457d5fdb31bab8e0b81141b02fda0e16446b7d86c502dd9b0353f'
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_ctype.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_ctype.o')==report['units'][0]['object_sha256']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_scanf_source_whitespace.py') and g['runtime_report_sha256']==sha(bp) and g['runtime_object_sha256']==sha(bp.parent/'native-scanf-runtime.o')==bundle['linked_sha256'] and not bundle['undefined_symbols']
 assert g['callback_comparisons']==84687 and g['trace_sha256']=='4623a2cd7c5171bcf455248c8f2ff9c8cd7fe4a1e963b18d9eb8f589b91c03e6'
 assert g['comparisons']==25910 and g['counts']=={'integer':10055,'string':3567,'getc':6144,'ungetc':6144} and g['all_nonzero_byte_prefixes_through_source_whitespace'] and g['source_native_ctype'] and not g['whitespace_callback_fixture'] and 'whitespace_fixture_source' not in g
 assert g['source_input_callbacks_and_digit'] and g['executed_store_observer_with_full_arena_reconciliation'] and g['unicorn_memory_write_hooks_disabled']
 assert g['report_sha256']==sha(BASE/'native-scanf-conversion/report.json') and g['object_sha256']==sha(BASE/'native-scanf-conversion/native_scanf_conversion.o') and g['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 for receipt in [r,g]:assert receipt['layout_sha256']==sha(ROOT/receipt['layout']) and not receipt['instruction_identity']
 assert not report['units'][0]['undefined'] and not report['application_linked'] and not report['instruction_identity']
 for data in [report,bundle]:
  for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x275ec,4),(0x275f0,4),(0x275f4,18),(0xbda90,257)]:
  assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
  if a in [0x275ec,0x275f4]:
   evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'));assert evidence['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and evidence['normalized_result']['body']['total_bytes']==n
 assert e['native_body_bytes']==22 and e['source_data_bytes']==r['source_owned_data_bytes']==257 and e['nonascii_space_indices']==r['nonascii_indices_classified_as_space'] and len(e['nonascii_space_indices'])==64 and not e['locked_ownership_changed'] and not e['shared_numeric_final_placement']
 assert e['ownership_semantics_qualification']['original_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x000275f4')
 from audit_source_frontier import section_bytes
 assert section_bytes(OUT/'native_ctype.o','.r1.ctype.window',executable=False)==raw[0xbda90-0x27000:0xbdb91-0x27000]
 print('Native ctype/source scanf whitespace authenticated: EOF/all bytes preserve raw lookup; shared data, frontend/ABI/image gates remain open')
if __name__=='__main__':audit()
