#!/usr/bin/env python3
"""Authenticate FlashDB control source, symbolic TBB data and native gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-flashdb-control';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_flashdb_control.py')==c['generator_sha256']
 parent=BASE/'native-internal-flash-read-frames';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-internal-flash-read-frames-runtime.o')==b['parent_object_sha256'] and sha(BASE/'native-flashdb-query-count/native_flashdb_query_count.o')==v['count_object_sha256']
 for filename,hk,uk in [('native-flashdb-control-runtime.o','linked_sha256','undefined_symbols'),('control-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==87 and b['closed_parent_imports']==['r1_health_sync_provider_00063694'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_control.py')==v['driver_sha256'] and v['comparisons']==5728 and v['counts']=={'returned':4734,'assertion_loop':971,'fault':23} and v['commands_checked']==259 and v['trace_sha256']=='814e87fe3ac9cb12b7fc873d8c50c89cbbe67a8d8142ea681fb22caf5b9df4fd'
 sections=allocated_sections(out/'native_flashdb_control.o');x=c['bodies'][0];assert len(c['bodies'])==1 and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==242 and c['native_jump_table_bytes']==12 and x['source_span_bytes']==384 and sections['.text.'+x['symbol']][2]==384 and sha(out/'disassembly-63694.txt')==x['disassembly_sha256']
 source=(ROOT/'r1/components/runtime/native_flashdb_control.c').read_text();assert source.count('.byte (FDI_')==12 and not any(0x636a2<=int(i['address'],16)<0x636ae for i in x['instructions'])
 table=raw[0x636a2-0x27000:0x636ae-0x27000];targets=[0x636a2+v*2 for v in table];assert targets==[0x636d0,0x636fc,0x63700,0x63704,0x63708,0x63738,0x63740,0x636fa,0x636fa,0x63746,0x636fa,0x63766]
 for name,addr,text in [('control_name',0x9bdd8,b'fdb_tsdb_control\0'),('control_filemode_error',0xc0a68,b'Error: set file mode Failed. Please defined the FDB_USING_FILE_MODE macro.\0')]:assert sections['.r1.fdb.'+name][2]==len(text) and sections['.r1.fdb.'+name][4]==hashlib.sha256(text).hexdigest() and raw[addr-0x27000:addr-0x27000+len(text)]==text
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==4 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==490
 r=json.loads((out/'rea-63694.json').read_text())['structuredContent'];n=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==384 and bytes.fromhex(n['bytes_hex'])==raw[0x63694-0x27000:0x63814-0x27000]
 up=json.loads((out/'upstream-contracts.json').read_text());assert up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and up['license']=='Apache-2.0'
 for p,h in up['files'].items():assert sha(ROOT/p)==h,p
 assert v['all_256_init_bytes_and_all_256_command_bytes_checked'] and v['independent_control_memory_mutation_oracle'] and v['actual_db_path_executes'] and v['printf_and_zero_low_rom_are_fixtures'] and v['jump_table_entries_are_symbolic_data_not_instruction_arrays']
 assert not v['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('FlashDB control:5728 comparisons;242 code+12 symbolic TBB bytes;476 new/490 joint verification bytes;87 imports;logging/ROM/history/image gates open')
if __name__=='__main__':audit()
