#!/usr/bin/env python3
"""Bind backend tests, single shared SVCI state and unresolved padding history."""
import hashlib,json,subprocess,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 from audit_source_frontier import section_bytes
 out=BASE/'native-dfu-backend-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text());probe=json.loads((out/'raw-frame-history-probe.json').read_text())
 assert r['comparisons']==74160 and r['counts']==dict(control=30720,sys=30720,response=5040,prepare=512,finalize=512,adv=4608,observer=2048) and r['observation_counts']==dict(hvx=41935,clear=2560,set=640,command=1168,handler=7680,callback=72660,power=160,mode=524,ring=130,sdk=98,copy=48) and r['trace_sha256']=='cbecbfb051392a274a9884dd39f0644680a2156f175f4d4dabbd48177eb8360e'
 for flag in ['actual_six_backend_bodies_memory_and_composed_hvc_observer','only_svc_svci_callback_power_logging_are_fixtures','canonical_and_backend_contexts_distinct_and_fresh_checked','all_control_opcodes_name_limits_and_fresh_copy_length_checked','response_api_frames_direct_raw_padding_and_hvx_length_checked','shared_svci_missing_pending_busy_and_result_paths_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','service_initialization_proven','physical_dfu_execution_proven','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_dfu_backend.py')==r['driver_sha256']==probe['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'dfu-backend-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(out/'dfu-backend-observer-source.o')==r['composed_object_sha256']==b['composed_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_dfu_backend_verification.ld')==r['layout_sha256']
 assert sha(out/'raw-frame-history-probe.json')==r['raw_frame_probe_sha256'] and not probe['matched'] and probe['kind']=='unused_hvx_frame_padding_history' and probe['api_visible_outputs_match'] and probe['no_padding_normalization'] and probe['different_cases']==r['raw_frame_difference_cases']==22
 native=bytes.fromhex(probe['native_raw_frames'][0]);source=bytes.fromhex(probe['source_raw_frames'][0]);assert len(native)==len(source)==24 and native[:23]==source[:23] and native[23]==0 and source[23]==0xaa
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-dfu-backend-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-dfu-backend-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==25 and b['closed_parent_imports']==['ble_dfu_buttonless_on_sys_evt','r1_dfu_bootloader_prepare_boundary','r1_dfu_control_point_write_boundary'] and b['newly_exposed_imports']==[]
 assert sha(out/'parent-shared-svci.o')==b['exported_parent_sha256'] and sha(out/'shared-dfu-data-source.o')==b['shared_data_object_sha256'] and sha(out/'shared-svci-source.o')==b['state_object_sha256'] and sha(out/'memory-source.o')==b['memory_object_sha256'] and sha(BASE/'native-dfu-ble-runtime/dfu-ble-source.o')==b['observer_object_sha256']
 assert undefined_symbols(out/'dfu-backend-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(out/'dfu-backend-observer-source.o')[0]==b['composed_undefined_symbols']
 parent=BASE/'native-dfu-ble-runtime/native-dfu-ble-runtime.o';exported=out/'parent-shared-svci.o';assert allocated_sections(parent)==allocated_sections(exported)==b['parent_allocated_sections']
 for obj in [parent,exported]:
  data=obj.read_bytes();offset=struct.unpack_from('<I',data,32)[0];size,count=struct.unpack_from('<HH',data,46);assert sum(bool(struct.unpack_from('<I',data,offset+i*size+8)[0]&2) for i in range(count))==len(b['parent_allocated_sections'])
 old=subprocess.check_output(['arm-none-eabi-nm','-S',str(parent)],text=True).splitlines();new=subprocess.check_output(['arm-none-eabi-nm','-S',str(exported)],text=True).splitlines();target='nrf_dfu_set_adv_name_svci_async_def'
 before=[s.split() for s in old if s.split()[-1:]==[target]];after=[s.split() for s in new if s.split()[-1:]==[target]];assert len(before)==len(after)==1 and before[0][0:2]==after[0][0:2] and int(before[0][1],16)==12 and before[0][2]=='b' and after[0][2]=='B'
 assert sorted(s for s in old if s.split()[-1:]!=[target])==sorted(s for s in new if s.split()[-1:]!=[target]) and b['export_transform']==['arm-none-eabi-objcopy','--globalize-symbol='+target] and b['existing_svci_state_reused']
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('52050',44),('5207c',24),('521d8',160),('522d8',84),('8ed5c',124),('52278',96),('c2a98',212),('c2b6c',206)]:
  q=json.loads((BASE/'native-dfu-backend'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 obj=BASE/'native-dfu-backend/native_dfu_backend.o';assert section_bytes(obj,'.r1.dfu.backend_context',executable=False)==bytes(4) and section_bytes(obj,'.r1.dfu.adv_name',executable=False)==bytes(28)
 for s,a,n in [('protected_ring',0xc2a98,212),('protected_sdk',0xc2b6c,206)]:assert section_bytes(obj,'.r1.dfu.'+s,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert cold[0x20007934-0x200064a8:0x20007938-0x200064a8]==bytes(4) and b['new_backend_pointer_bytes']==4 and b['new_adv_name_bytes']==28 and not b['service_initialization_proven'] and not b['physical_dfu_execution_proven']
 print('DFU backend:74160 API/RAM cases;six bodies;shared12-byte SVCI state;25 imports;22 raw-padding histories remain explicitly open')
if __name__=='__main__':audit()
