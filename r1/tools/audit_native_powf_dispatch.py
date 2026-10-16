#!/usr/bin/env python3
"""Audit powf dispatch while enforcing the explicit unresolved-core gate."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-powf-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');g=read(OUT/'consumer-verification.json');ev=read(OUT/'evidence.json');report=read(OUT/'report.json');bp=BASE/'native-powf-dispatch-runtime/report.json';bundle=read(bp);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert r['comparisons']==427168 and r['counts']=={'powf':427168} and r['trace_sha256']=='5b07862522891d3e21365cca57afaebf4436dcaf3ba32adea5430a22da0cc091'
 assert g['comparisons']==1952 and g['trace_sha256']=='7bff884f728c564c12614203f8c47c1958689431710f1fde535eaecabbc8cd22' and g['helper_observations']['compiled_entries']['powf']==144
 for receipt,driver in [(r,'verify_native_powf_dispatch.py'),(g,'verify_native_powf_dispatch_consumers.py')]:
  assert receipt['driver_sha256']==sha(ROOT/'r1/tools'/driver) and "'-fshort-enums'" in (ROOT/'r1/tools'/driver).read_text()
  assert receipt['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
  assert not receipt['runtime_no_unresolved'] and receipt['native_powf_core_fixture'] and not receipt['source_powf_complete'] and receipt['unresolved_source_provider']=='r1_powf_reduced' and not receipt['instruction_identity']
  assert receipt['runtime_report_sha256']==sha(bp) and receipt['runtime_object_sha256']==sha(bp.parent/'native-powf-dispatch-runtime.o')==bundle['linked_sha256']
  assert receipt['fixture_source']=='r1/tools/fixtures/powf_reduced_native_fixture.c' and receipt['fixture_source_sha256']==sha(ROOT/receipt['fixture_source'])
  assert receipt['layout']==ev['verification_layout'] and receipt['layout_sha256']==ev['verification_layout_sha256']==sha(ROOT/receipt['layout']) and receipt['parent_layouts']==ev['parent_layouts']
  for p,h in receipt['parent_layouts'].items():assert sha(ROOT/p)==h,p
 assert bundle['undefined_symbols']==['r1_powf_reduced'] and not bundle['application_linked']
 for rp in [report,bundle]:
  for p,h in rp['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in bundle['provider_reports'].items():assert sha(BASE/p)==h,p
 for p,h in bundle['objects'].items():assert sha(BASE/p)==h,p
 assert r['report_sha256']==sha(OUT/'report.json') and r['object_sha256']==sha(OUT/'native_powf_dispatch.o')
 for p,h in r['evidence'].items():assert sha(OUT/p)==h,p
 for flag in ['all_binary32_exponents','both_signs','seeded_random_pairs','all_four_rounding_modes','float_flush_to_zero_and_default_nan_modes','initial_inexact_flag_zero_and_one','return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked','actual_source_powf_dispatch','base_and_exponent_signs','integer_parity_cases','independent_calls_reset_xpsr','signed_zero_and_infinity_pairs']:assert r[flag]
 for a,n in [(0x3a620,922),(0x3a9bc,124),(0x3aa88,478),(0x3ac68,16)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
 raw=read(OUT/'rea-3a620.json')['structuredContent'];assert raw['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and raw['normalized_result']['body']['total_bytes']==1524 and raw['normalized_result']['body']['ranges']==[{'start':'0x3a620','end':'0x3a9b9'},{'start':'0x3a9bc','end':'0x3aa37'},{'start':'0x3aa88','end':'0x3ac65'}]
 from audit_source_frontier import section_bytes
 data=section_bytes(OUT/'native_powf_dispatch.o','.r1.math.powf_dispatch_data',executable=False);assert data==app.read_bytes()[0x13c68:0x13c78] and len(data)==r['source_owned_numeric_bytes']==ev['source_owned_numeric_bytes']==16 and hashlib.sha256(data).hexdigest()==r['source_owned_data_sha256']
 assert ev['new_source_routes_admitted']==0 and ev['dispatcher_native_bytes']==580 and ev['pending_core_native_bytes']==944 and ev['full_native_body_bytes']==1524
 contract=read(OUT/'core-contract.json');assert sha(OUT/'core-contract.json')==ev['core_contract_sha256'] and not contract['external_blocker'] and contract['native_entry']=='0x3a65c' and contract['pending_core_native_bytes']==944
 for row in contract['pointer_contracts']:
  a=int(row['address'],16);assert (int.from_bytes(app.read_bytes()[a-0x27000:a-0x27000+4],'little')+int(row['pc'],16))&0xffffffff==int(row['target'],16)
 assert ev['core_table_evidence_sha256']==sha(OUT/'core-table-evidence.json')
 for name,h in read(OUT/'core-table-evidence.json').items():assert sha(OUT/name)==h
 for a,n in [(0x3aa38,80),(0x3ac78,16),(0xbd950,128),(0xbd9d0,64),(0xbda10,64),(0xbda50,64)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
 ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert sha(ledger)==ev['ownership_sha256']=='3ac7de261785d461c3af637fa3d6af46170917f4a9f329bf6aa6bae2ecc4ea13' and ev['ownership_row']==next(row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry']=='0x0003a620') and not ev['locked_ownership_changed']
 assert ev['pseudocode_sha256']==sha(ROOT/ev['pseudocode_source']) and ev['pseudocode_slice_sha256']==sha(OUT/'pseudocode-3a620.c.txt')
 for name,receipt in [('verification.json',r),('consumer-verification.json',g)]:
  initial=read(OUT/('initial-'+name));assert initial['comparisons']==receipt['comparisons'] and initial['trace_sha256']==receipt['trace_sha256']
 print('Powf dispatcher verified with native core fixture; one unresolved source core remains and frontier is not promoted')
if __name__=='__main__':audit()
