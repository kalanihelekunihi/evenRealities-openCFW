#!/usr/bin/env python3
"""Authenticate native LIS identity and request composition evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-lis-identity';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==2592 and all(v==432 for v in r['counts'].values()) and len(r['counts'])==6 and r['observation_counts']==dict(bus_read=432,bus_write=288,custom_read=432) and r['trace_sha256']=='4cb5489e5433a99974ede3eb56bc0dc66918077e7541ab6b790ca24d899d261b'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'identity-source.o')==r['graph_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_identity.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for flag in ['actual_identity_device_id_defaults_requests_registry_and_memclr','only_bus_and_custom_register_callbacks_are_fixtures','request_record_bytes_and_pointer_checked','callee_sp_context_ram_and_identity_saved_r3_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 parent=BASE/'native-lis-fifo-runtime';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-fifo-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native_lis_identity.o')==b['unit_object_sha256'] and sha(out/'native-lis-identity-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-lis-identity-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==29 and not undefined_symbols(out/'identity-source.o')[0]
 assert b['closed_parent_imports']==['r1_lis2dw12_identity_probe'] and not b['newly_exposed_imports'] and not b['whole_image_complete'] and not b['instruction_identity'] and not b['hardware_write_executed']
 print('LIS identity/default requests:2592 comparisons; native context and request-pointer contracts authenticated')
if __name__=='__main__':audit()
