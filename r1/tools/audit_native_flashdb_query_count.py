#!/usr/bin/env python3
"""Authenticate scoped FlashDB receipts without importing emulation drivers."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-flashdb-query-count';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==v['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==v['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 parent=BASE/'native-health-notification-stages';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-notification-stages-runtime.o')==b['parent_object_sha256']
 for filename,hashkey,ukey in [('native-flashdb-query-count-runtime.o','linked_sha256','undefined_symbols'),('query-count-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hashkey] and undefined_symbols(out/filename)[0]==b[ukey]
 assert len(b['undefined_symbols'])==89 and b['closed_parent_imports']==['r1_health_sync_provider_00063cb4'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_query_count.py')==v['driver_sha256'] and v['comparisons']==8192 and v['exact_bytes']==171 and v['trace_sha256']=='5fd20905029843299de5c378b5649474759842d4f55054dd5d4b511de1dab9f9'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(app.read_bytes()[a:a+x['length']]).hexdigest()==x['sha256']
 assert v['actual_source_db_path_executed'] and v['iterator_and_printf_are_fixtures'] and not v['iterator_callback_execution_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 k=BASE/'native-flashdb-tsdb-kernels';kb=json.loads((k/'build.json').read_text());kv=json.loads((k/'verification.json').read_text());up=json.loads((k/'upstream-slices.json').read_text());source=ROOT/up['source'];assert sha(source)==up['source_sha256']
 for x in up['slices']:assert hashlib.sha256(source.read_text()[x['start']:x['end']].encode()).hexdigest()==x['slice_sha256']
 assert kb['upstream_pin']==up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and kb['license']==up['license']=='Apache-2.0'
 assert sha(ROOT/'r1/components/runtime/native_flashdb_tsdb_kernels.c')==kb['source_sha256']==kv['source_sha256'] and sha(k/'native_flashdb_tsdb_kernels.o')==kb['object_sha256']==kv['object_sha256']
 assert sha(k/'upstream-slices.json')==kb['upstream_slices_sha256']==kv['upstream_slices_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_tsdb_kernels.py')==kv['driver_sha256']
 assert kv['comparisons']==50000 and kv['trace_sha256']=='45f65b15975c09eae6f3a1cd7c0120745dd8752e41a94904700151c8080beb35' and not kv['raw_abi_verified'] and not kv['main_provider_graph_linked']
 rea=json.loads((k/'rea-count-callback.json').read_text())['structuredContent'];assert rea['normalized_result']['complete'] and bytes.fromhex(rea['normalized_result']['bytes_hex'])==app.read_bytes()[0x87428-0x27000:0x8743a-0x27000]
 print('FlashDB count:8192 cases;171 exact verification bytes;89 imports; upstream kernels50000 typed comparisons;iterator/raw ABI/image gates open')
if __name__=='__main__':audit()
