#!/usr/bin/env python3
"""Audit source scatter providers and source-handler region configuration."""
import csv,hashlib,json,re,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scatter-data';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_scatter_data.o'
 assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a' and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_scatter_data.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and not report['units'][0]['undefined']
 assert r['comparisons']==127394 and r['counts']['decompress']==127135 and r['trace_sha256']=='8e4e448b19cce852280d4e8fb0ba54bcd5dba4d56f6bae27cd9c56de3001a1db'
 assert r['comparisons']==sum(r['counts'].values()) and r['counts']['zero']==257 and r['counts']['official_decompress']==r['counts']['official_zero']==1
 assert r['layout_sha256']==sha(ROOT/r['layout']) and not r['instruction_identity'] and not report['application_linked'] and not report['instruction_identity']
 for flag in ['return_stack_callee_integer_full_ram_and_nonstack_write_order_checked','executed_store_observer_with_full_ram_reconciliation','unicorn_memory_write_hooks_disabled','candidate_native_code_execution_forbidden','all_token_bytes','extended_literal_and_run_boundaries','overlapping_backreference_and_distance_zero','zero_output_size_still_processes_token','word_zero_lengths_multiple_of_four','compressed_initialization_data_is_authenticated_fixture']:assert r[flag]
 assert not r['initialized_data_source_ownership'] and r['official_compressed_bytes']==1784 and r['official_initialized_bytes']==6492 and r['official_zero_bytes']==213172
 assert r['observed_initialized_data_sha256']=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 assert r['observed_initialized_data_sha256']==sha(OUT/'observed-initialized-data.bin') and (OUT/'observed-initialized-data.bin').stat().st_size==6492
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x283a0,36),(0x286f4,86),(0x3bc68,14),(0xc43ec,32),(0xc4610,1784)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x283a0,0x286f4,0x3bc68]:
  evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'));assert evidence['error']['code']=='invalid_request' and 'No procedure exists' in str(evidence)
 assert e['native_decompress_bytes']==86 and e['native_zero_bytes']==14 and e['native_dispatch_bytes']==28 and e['native_dispatch_literals_bytes']==8 and e['locked_scatterload_extent_bytes']==846==28+8+e['manual_scanf_core_bytes_within_extent'] and not e['locked_ownership_changed']
 assert not e['compressed_initialization_source_ownership'] and not e['scatter_dispatcher_source_complete'] and not e['startup_continuation_source_complete']
 assert e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')
 assert not any(row['image']=='application' and row['entry']=='0x0003bc68' for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()))
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)/'regions.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.scatter.regions','-O','binary',str(obj),str(p)],check=True);data=p.read_bytes();assert len(data)==32
  for offset in [0,16]:assert data[offset:offset+12]==raw[0xc43ec-0x27000+offset:0xc43ec-0x27000+offset+12]
 relocations=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_ABS32)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.r1.scatter.regions',str(obj)],text=True),re.M)
 assert relocations==[('0000000c','R_ARM_ABS32','r1_native_scatter_decompress'),('0000001c','R_ARM_ABS32','r1_native_scatter_zero')]
 consumed=read(OUT/'input-consumption.json');assert consumed['driver_sha256']==sha(ROOT/'r1/tools/inspect_native_scatter_input.py') and consumed['application_sha256']==sha(app) and consumed['initialized_sha256']==r['observed_initialized_data_sha256'] and consumed['available_fixture_bytes']==1784 and not consumed['source_ownership']
 assert e['input_consumption_sha256']==sha(OUT/'input-consumption.json') and e['supplemental_zero_provider_not_in_locked_ledger']
 assert consumed['consumed_bytes']==e['consumed_compressed_bytes']==1781 and consumed['trailing_bytes']=='000000' and e['trailing_alignment_bytes']==3
 assert 0<=consumed['consumed_bytes']<=1784 and len(bytes.fromhex(consumed['trailing_bytes']))==1784-consumed['consumed_bytes']
 print('Source scatter providers/region callbacks authenticated; compressed data ownership, dispatcher/startup and ABI/image gates remain open')
if __name__=='__main__':audit()
