#!/usr/bin/env python3
"""Audit native PRNG/parser primitives and preserve manual-boundary evidence."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-libc-primitives';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert r['counts']=={'rand':1284,'srand':1284,'digit':21798,'getc':1280} and r['comparisons']==25646 and r['trace_sha256']=='d6c484c55230f4b1b4f66b7024d5b6fc2e48a036553b54121cfbe8d783688213'
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_libc_primitives.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_libc_primitives.o')==report['units'][0]['object_sha256']
 assert r['layout_sha256']==sha(ROOT/r['layout']) and not report['units'][0]['undefined'] and not report['application_linked'] and not report['instruction_identity'] and not r['instruction_identity']
 for flag in ['return_stack_callee_integer_and_nonstack_writes_checked','all_byte_digit_values','malformed_unsigned_digit_inputs','all_byte_getc_values','zero_negative_and_wrapping_cursor_advances','seeded_random_prng_states','source_complete_for_selected_bodies','runtime_no_unresolved']:assert r[flag]
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x276a4,20),(0x276b8,6),(0x27ff4,28),(0x28010,12),(0x276c0,8)]:
  assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
  if a==0x276c0:continue
  evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'))
  if a in [0x27ff4,0x28010]:
   assert evidence['error']['code']=='invalid_request' and 'No procedure exists' in str(evidence)
  else:
   assert evidence['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and evidence['normalized_result']['body']['total_bytes']==n
 assert struct.unpack_from('<II',raw,0x276c0-0x27000)==(0x20007db0,0x41c64e6d) and e['native_body_bytes']==66 and not e['startup_seed_ownership']
 assert raw[0x28000-0x27000:0x28002-0x27000]==bytes.fromhex('01d3')
 print('Native PRNG/parser primitives authenticated: 25646 cases; startup, full ABI and image gates remain open')
if __name__=='__main__':audit()
