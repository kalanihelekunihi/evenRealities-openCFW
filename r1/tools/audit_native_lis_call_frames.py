#!/usr/bin/env python3
"""Authenticate native LIS call bridges and composed/direct regression receipts."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-lis-call-frames';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());parent=BASE/'native-lis-configure';po=parent/'native-lis-configure-runtime.o';clone=out/'parent-weak.o'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['parent_clone_sha256'] and allocated_sections(po)==allocated_sections(clone) and b['parent_allocated_sections_identical']
 def nm(path):return {v[2]:(v[0],v[1]) for line in subprocess.check_output(['arm-none-eabi-nm',str(path)],text=True).splitlines() if len(v:=line.split())==3}
 before,after=nm(po),nm(clone);names=b['only_named_symbol_bindings_weakened'];assert len(names)==len(set(names))==22 and set(before)==set(after)
 for name,v in before.items():assert after[name]==(v[0],'W') if name in names else after[name]==v
 linked=out/'native-lis-call-frames-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==28 and sha(out/'configure-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'configure-source.o')[0]==b['graph_undefined_symbols']
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 assert not undefined_symbols(out/'st-field-updates.o')[0] and b['upstream_pin']=='8d4bd522015004a9646102702901ba5a15ec6d39' and b['upstream_license']=='BSD-3-Clause' and not b['unmodified_upstream_body'] and not b['exact_vendor_checkout_proven']
 vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+b['upstream_pin']);raw=(vendor/'lis2dw12_reg.c').read_bytes();generated=(out/'st-field-updates.c').read_text();assert (vendor/'LICENSE').read_text() in generated and len(b['source_assignments'])==20
 for row in b['source_assignments']:
  original=raw[row['start']:row['end']];assert hashlib.sha256(original).hexdigest()==row['original_slice_sha256'] and row['assignment'] in original.decode() and row['assignment'].replace(row['local']+'.','u.reg.') in generated and row['helper'] in generated
 assert r['comparisons']==51840 and r['counts']==dict(id_missing=46080,reset_timeout=1152,configured=4608) and r['observation_counts']==dict(read=65664,write=23616,custom_read=37440,delay=29376,mode=125952,ring=31488,sdk=23616) and r['trace_sha256']=='2c806975de2871743390be1f09e04d1d604e774ac99f92c0760144eb62297e1d'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'configure-source.o')==r['graph_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_call_frames.py')==r['driver_sha256'] and sha(parent/'rea-configure-bytes.json')==r['evidence']['rea-configure-bytes.json']
 for flag in ['actual_configure_native_call_bridges_pure_st_helpers_fifo_default_transport_and_registry','only_bus_custom_read_delay_and_logging_callbacks_are_fixtures','reset_boundary_fresh_log_mode_odr_and_fifo_drain_checked','raw_r0_callee_sp_context_and_outer_frame_checked']:assert r[flag]
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for key,count,trace,obj in [('registers',55767,'8eaf8ead8309d76e4348105b2b5587c298a34f63d43ca84b8ea3e122e6313763','registers-source.o'),('setup',26000,'d53fcefa6458c4852fe50e6ddf2433511f10c0749ea7f8564ab1fbbb62d850ec','setup-source.o'),('fifo',12652,'c24624b34d55085ea5250d1e58e61071ea228d9b081c89aca80c264a864c22ae','lis-fifo-source.o')]:
  d=out/('direct-'+key);proof=json.loads((d/'verification.json').read_text());dr=json.loads((d/'report.json').read_text());assert proof['comparisons']==count and proof['trace_sha256']==trace and sha(d/'report.json')==proof['report_sha256'] and sha(d/obj)==dr['graph_object_sha256']==b['linked_sha256'] and dr['parent_call_frames_report_sha256']==sha(out/'report.json') and proof['application_sha256']==sha(app) and sha(ROOT/('r1/tools/verify_native_lis_call_frames_'+key+'.py'))==proof['driver_sha256']
  assert (proof['graph_sha256'] if key!='fifo' else proof['object_sha256'])==sha(d/obj)
  for path,h in dr['inputs'].items():assert sha(ROOT/path)==h,path
  assert not proof['whole_image_complete'] and not proof['instruction_identity'] and not proof['hardware_write_executed']
 failure=json.loads((parent/'composed-frame-probe.json').read_text());assert not failure['bus_request_pointer_matches'] and not failure['composed_runtime_verified'] and failure['first_native_observation'][1][2]==0x2003cf80 and failure['first_source_observation'][1][2]==0x2003cf70
 print('LIS call-frame fix:51840 composed +94419 direct comparisons; native API pointers match; old failure retained')
if __name__=='__main__':audit()
