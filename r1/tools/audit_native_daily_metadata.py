#!/usr/bin/env python3
"""Authenticate daily metadata and signed-day helpers with explicit provider gaps."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-daily-metadata';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-daily-metadata-runtime/report.json';b=read(rp);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['backend_calls_per_side']==53248 and r['logger_calls_per_side']==9216 and r['trace_sha256']=='febe4eb1c4c84007c3e69cbbad2c0876c548ea3674599f5ace3dd19881ff12b6'
 assert r['comparisons']==57344 and len(r['counts'])==14 and all(n==4096 for n in r['counts'].values())
 for flag in ['actual_source_day_offset_backend_and_u64_division','backend_and_logging_are_named_fixtures','controlled_timezone_and_logger_mutations_are_fixtures','raw_r0_callee_sp_and_full_observed_nonstack_ram_checked','no_native_candidate_body_execution']:assert r[flag]
 assert '__aeabi_ldivmod' in read(OUT/'report.json')['units'][0]['undefined'] and '__aeabi_uldivmod' not in read(OUT/'report.json')['units'][0]['undefined']
 assert not r['instruction_identity'] and not r['physical_clock_or_cache_verified'] and not r['whole_image_complete'] and r['source_metadata_fields_bytes']==36
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_daily_metadata.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['metadata_object_sha256']==sha(rp.parent/'daily-metadata-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_daily_metadata_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['time_provider_object_sha256']==sha(rp.parent/'time-provider-source.o') and b['linked_sha256']==sha(rp.parent/'native-daily-metadata-runtime.o') and b['metadata_undefined_symbols']==['nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get'] and len(b['undefined_symbols'])==54
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'daily-metadata-source.o')[0]==b['metadata_undefined_symbols'] and undefined_symbols(rp.parent/'native-daily-metadata-runtime.o')[0]==b['undefined_symbols']
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for p in OUT.glob('ghidra-*.json'):
  g=read(p);a=int(g['address'],16);assert bytes(g['data'])==raw[a-0x27000:a-0x27000+g['length']]
 for p in OUT.glob('rea-*.json'):
  q=read(p);q=q.get('structuredContent') or json.loads(next(x['text'] for x in q['content'] if x['type']=='text'));a=int(p.stem.split('-')[1],16)
  if a in [0x8ad64,0x8adb4]:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==(44 if a==0x8ad64 else 8)
  else:assert 'No procedure exists' in str(q)
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 ownership=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['ownership_rows'])==14 and all(row in ownership for row in e['ownership_rows']) and sum(int(row['size']) for row in e['ownership_rows'])==264
 from audit_source_frontier import section_bytes
 obj=OUT/'native_daily_metadata.o'
 assert section_bytes(rp.parent/'time-provider-source.o','.text.__udivmoddi4')==section_bytes(BASE/'integer-runtime/udivmoddi4.o','.text.__udivmoddi4')
 for name,ts,off in e['metadata_cells']:
  assert 0x20007e04<=ts<0x20007e04+0x340b4 and 0x20007e04<=off<0x20007e04+0x340b4
  assert section_bytes(obj,f'.r1.daily.{name}.timestamp',executable=False)==bytes(4) and section_bytes(obj,f'.r1.daily.{name}.offset',executable=False)==bytes(2)
 assert section_bytes(obj,'.r1.daily.hr.ring',executable=False)==b'[RING]hr db init: %d\0' and section_bytes(obj,'.r1.daily.hr.sdk',executable=False)==b'hr db init: %d\0'
 initial=OUT/'initial-unsigned-day-candidate';m=read(initial/'manifest.json')
 for p,h in m['files'].items():assert sha(initial/p)==h,p
 assert e['native_signed_division_entry']=='0x2754a' and e['native_local_day_offset_captured_before_backend'] and e['metadata_offset_reloaded_after_backend'] and e['stress_uses_backend_timestamp'] and not e['surrounding_cache_structures_owned'] and not e['whole_image_identity']
 print('Daily metadata authenticated:57344 comparisons;54 startup imports remain;backend/logger fixtures,REA gaps,private ABI,image gates explicit')
if __name__=='__main__':audit()
