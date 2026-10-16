#!/usr/bin/env python3
"""Audit native sorting/string bodies without upgrading bounded behavior to image proof."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-libc-sequences';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert r['counts']=={'qsort':1824,'strcat':25,'strncpy':510,'memcmp':66080,'strtok':42} and r['comparisons']==68481 and r['callback_comparisons']==213646 and r['trace_sha256']=='df74a03b3eb38242e8f7793ba85542db8cfc8062fdef9eafba5d9c66388f779c'
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_libc_sequences.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_libc_sequences.o')==report['units'][0]['object_sha256']
 assert r['layout_sha256']==sha(ROOT/r['layout']) and not report['units'][0]['undefined'] and not report['application_linked'] and not report['instruction_identity'] and not r['instruction_identity']
 for flag in ['return_stack_callee_integer_full_arena_and_nonstack_write_order_checked','qsort_callback_transcripts_checked','qsort_comparator_fixture','all_first_byte_memcmp_pairs','strncpy_padding_and_truncation','strtok_ten_call_continuations','runtime_no_unresolved']:assert r[flag]
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x27606,156),(0x277c0,24),(0x277d8,24),(0x2781a,26),(0x27854,62),(0x27894,4)]:
  assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
  if a==0x27894:continue
  evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'))
  assert evidence['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and evidence['normalized_result']['body']['total_bytes']==n
 assert struct.unpack_from('<I',raw,0x27894-0x27000)[0]==0x20007db4 and e['native_body_bytes']==292 and not e['startup_cursor_ownership']
 assert e['initial_counterexample_sha256']==sha(OUT/'initial-write-order-counterexample.log') and "'qsort', '8a08'" in (OUT/'initial-write-order-counterexample.log').read_text()
 print('Native sorting/string sequences authenticated: 68481 cases and 213646 callback comparisons; ABI/startup/image gates remain open')
if __name__=='__main__':audit()
