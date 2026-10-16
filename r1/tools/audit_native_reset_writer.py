#!/usr/bin/env python3
"""Bind reset writer receipts to source, providers and independently read native spans."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-reset-writer';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=BASE/'native-reset-writer-runtime/report.json';b=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert r['comparisons']==36864 and r['counts']=={'byte':24576,'lr':1536,'clear':1536,'pc':1536,'caller':1536,'tag':1536,'capture':1536,'current':1536,'probe':1536}
 assert r['events_per_side']==294840 and r['trace_sha256']=='3b622338ba6a4fc7233c6edbbc1fa1c21984eccd73ad7e5dc9f9dee5ad728366'
 for flag in ['actual_source_crc_and_attributable_clear','probe_source_bytes_match','candidate_native_execution_forbidden_except_source_probe','controlled_context_and_record_mutation_fixtures','raw_r0_callee_registers_stack_and_observed_ram_checked']:assert r[flag]
 assert not r['instruction_identity'] and not r['full_image_complete']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_reset_writer.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['writer_object_sha256']==sha(rp.parent/'reset-writer-source.o') and r['application_sha256']==sha(app) and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_reset_writer_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['clear_object_sha256']==sha(rp.parent/'eabi-clear-source.o') and b['linked_sha256']==sha(rp.parent/'native-reset-writer-runtime.o') and b['writer_undefined_symbols']==[] and len(b['undefined_symbols'])==61 and b['remaining_application_imports']==[] and len(b['application_imports_resolved'])==13
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'reset-writer-source.o')[0]==[] and undefined_symbols(rp.parent/'native-reset-writer-runtime.o')[0]==b['undefined_symbols']
 for group in ['rea','ghidra']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 spans=[(0x7ee30,70),(0x7eeda,44),(0x7ef06,70),(0x7efaa,44),(0x7efd6,20),(0x7effe,24),(0x7efea,20),(0x58a9a,30),(0x27484,4),(0x7ee78,4)]
 for a,n in spans:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a,n in spans[:-1]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));body=rea['normalized_result']['body'];assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
  expected=[{'start':'0x58a9a','end':'0x58ab7'},{'start':'0x7eeda','end':'0x7ef05'}] if a in [0x58a9a,0x7eeda] else [{'start':hex(a),'end':hex(a+n-1)}];assert body['ranges']==expected and body['total_bytes']==(74 if a in [0x58a9a,0x7eeda] else n)
 ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';assert e['ownership_sha256']==sha(ownership) and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and len(e['ownership_rows'])==8 and e['unique_native_bytes']==326 and not e['folded_return_address_tail_separate_row'] and not e['whole_image_identity']
 rows=list(csv.DictReader(ownership.open()));assert all(x in rows for x in e['ownership_rows'])
 print('Reset writer source authenticated:',r['comparisons'],'cases;61 transitive startup imports remain; physical/private ABI/image gates open')
if __name__=='__main__':audit()
