#!/usr/bin/env python3
"""Authenticate source-owned cache cells/names and actual-registry tests."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from audit_source_frontier import section_bytes
 out=BASE/'native-peripheral-bindings-runtime';unit=BASE/'native-peripheral-bindings/native_peripheral_bindings.o';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==6560 and r['counts']==dict(r1_led_ldo_device_bind=640,r1_motion_bus_device_bind=160,r1_motion_interrupt_input_lookup=640,r1_ppg_device_bind=2560,r1_touch_device_bind=2560) and r['observation_counts']==dict(find=14240,dispatch=5120,open=1728) and r['trace_sha256']=='ba718da8b0b15f4141d40017f61e89544ceb20abe5db569b186409bd723b0502'
 for flag in ['actual_registry_strcmp_and_dispatch','only_open_operation_is_fixture','all_local_presence_cache_masks_checked','repeated_calls_and_mutating_lookup_open_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_raw_abi_verified','cross_call_private_frame_history_verified','whole_context_owned','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['new_zero_handle_bytes']==40 and r['new_owned_string_bytes']==100
 assert sha(ROOT/'r1/tools/verify_native_peripheral_bindings.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'peripheral-bindings-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_peripheral_bindings_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-peripheral-bindings-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-peripheral-bindings-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==38
 assert undefined_symbols(out/'peripheral-bindings-source.o')[0]==b['graph_undefined_symbols']==[]
 assert b['closed_parent_imports']==['r1_led_ldo_device_bind','r1_motion_interrupt_input_lookup','r1_ppg_device_bind','r1_touch_device_bind'] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for prefix,items in [('bytes',[('50128',24),('50150',20),('502c4',32),('50944',48),('51310',44)]),('data',[('50140',14),('50164',10),('502e4',29),('50974',33),('5133c',41)])]:
  for a,n in items:
   q=json.loads((BASE/'native-peripheral-bindings'/('rea-'+prefix+'-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
   assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 cells=[('r1_motion_irq_device',0x200076b0),('r1_motion_bus_device',0x200076b4),('r1_led_enable_device',0x20007688),('r1_touch_ldo_device',0x2000768c),('r1_ppg_bus_device',0x200076cc),('r1_ppg_irq_device',0x200076d0),('r1_ppg_reset_device',0x200076d8),('r1_touch_bus_device',0x200067fc),('r1_touch_output_device',0x20006800),('r1_touch_input_device',0x20006804)]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 for n,a in cells:assert section_bytes(unit,'.r1.bind.'+n,executable=False)==bytes(4)==cold[a-0x200064a8:a-0x200064a8+4]
 names=[(0x50144,10),(0x50168,6),(0x502e8,11),(0x502f4,13),(0x50978,6),(0x50980,8),(0x50988,13),(0x51340,6),(0x51348,14),(0x51358,13)]
 for i,(a,n) in enumerate(names):assert section_bytes(unit,'.r1.bind.name'+str(i),executable=False)==raw[a-0x27000:a-0x27000+n]
 rows={int(q['entry'],16):q for q in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open())}
 for a,n in [(0x50128,24),(0x502c4,32),(0x50944,48),(0x51310,44)]:assert int(rows[a]['size'])==n
 for p,h in json.loads((out/'superseded-evidence.json').read_text()).items():assert sha(out/p)==h,p
 print('Peripheral bindings:6560 cases;actual registry/dispatch;40 handle+100 name bytes;38 imports;context/ABI/image gates open')
if __name__=='__main__':audit()
