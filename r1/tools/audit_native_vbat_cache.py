#!/usr/bin/env python3
"""Authenticate ADC cache source, bounded graph and explicit REA boundary gap."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-vbat-cache';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-vbat-cache-runtime/report.json';b=read(rp);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['workflows']==1792 and r['calls_per_workflow']==3 and r['find_calls_per_side']==3275 and r['strcmp_calls_per_side']==6048 and r['trace_sha256']=='551c476aa5633665d855a5e2d2be88e317d6570619db80487089b0b2d7be2594'
 for flag in ['actual_source_registry_and_strcmp','controlled_mutations_are_fixtures','full_observed_nonstack_ram_raw_r0_callee_and_sp_checked','no_native_candidate_body_execution']:assert r[flag]
 assert not r['instruction_identity'] and not r['physical_adc_verified'] and not r['whole_image_complete']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_vbat_cache.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['cache_object_sha256']==sha(rp.parent/'vbat-cache-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_vbat_cache_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['registry_object_sha256']==sha(rp.parent/'registry-source.o') and b['linked_sha256']==sha(rp.parent/'native-vbat-cache-runtime.o') and b['cache_undefined_symbols']==[] and len(b['undefined_symbols'])==60
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'vbat-cache-source.o')[0]==[] and undefined_symbols(rp.parent/'native-vbat-cache-runtime.o')[0]==b['undefined_symbols']
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for a,n in [(0x9143c,20),(0x91450,4),(0x91454,9)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 rea=read(OUT/'rea-9143c.json');assert rea['isError'] and 'No procedure exists' in str(rea) and e['rea_boundary_recovered']==False
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 ownership=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_row']==next(x for x in ownership if x['image']=='application' and x['entry']=='0x0009143c')
 from audit_source_frontier import section_bytes
 obj=OUT/'native_vbat_cache.o';cold=ROOT/e['cold_observation'];assert section_bytes(obj,'.r1.vbat.cache',executable=False)==cold.read_bytes()[0x3f8:0x3fc]==bytes(4) and section_bytes(obj,'.r1.vbat.name',executable=False)==b'vbat_adc\0'
 assert e['source_owned_cache_bytes']==4 and e['native_body_bytes']==20 and not e['surrounding_state_owned'] and not e['whole_image_identity']
 print('ADC cache authenticated:1792 three-call source registry/string workflows;60 startup imports remain;REA boundary/physical/image gates explicit')
if __name__=='__main__':audit()
