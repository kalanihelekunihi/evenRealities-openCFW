#!/usr/bin/env python3
"""Bind asymmetric callbacks and upstream CMSIS state query to receipts."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-hw-twi-completion-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==66624 and r['counts']==dict(matrix=61440,mutation=5184) and r['observation_counts']==dict(scheduler=43840,release=18304,null_release=384) and r['trace_sha256']=='c64bb7740f08b18aefb3d588b62dcd79a7f7f8ac4e7ac52dffa91fa3fe302008'
 for flag in ['actual_irq_and_pinned_cmsis_kernel_query','only_scheduler_and_semaphore_release_are_fixtures','all_event_bytes_and_bus_flag_asymmetry_checked','fresh_handle_after_state_query_checked','repeated_event_calls_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_raw_abi_verified','cross_call_private_frame_history_verified','physical_irq_and_semaphore_delivery_proven','metadata_callback_abi_migrated','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_hw_twi_completion.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'hw-completion-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_hw_twi_completion_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-hw-twi-completion-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-hw-twi-completion-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==36
 assert sha(out/'kernel-state-source.o')==b['kernel_object_sha256'] and undefined_symbols(out/'kernel-state-source.o')[0]==['xTaskGetSchedulerState'] and undefined_symbols(out/'hw-completion-source.o')[0]==b['graph_undefined_symbols']
 # Compare pre-relocation instructions; the shared section reader deliberately
 # rejects relocation-bearing sections, so extract these two explicitly.
 with tempfile.TemporaryDirectory() as tmp:
  extracted=[]
  for i,obj in enumerate([out/'kernel-state-source.o',BASE/'rtos-semaphore-new/cmsis_os2.o']):
   dest=Path(tmp)/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.text.osKernelGetState','-O','binary',str(obj),str(dest)],check=True);extracted.append(dest.read_bytes())
  assert len(extracted[0])==38 and extracted[0]==extracted[1]
 nm=subprocess.check_output(['arm-none-eabi-nm','-S',str(out/'native-hw-twi-completion-runtime.o')],text=True).splitlines();rows=[x.split() for x in nm if x.split()[-1:] == ['KernelState']];assert len(rows)==1 and int(rows[0][1],16)==4 and rows[0][2]=='b'
 assert b['cmsis_kernel_state_source_bytes']==4 and not b['canonical_kernel_state_final_placement_proven'] and b['closed_parent_imports']==['r1_hw_twi0_irq','r1_hw_twi1_irq'] and b['newly_exposed_imports']==[]
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('70778',84),('707cc',80),('7d26c',32)]:
  q=json.loads((BASE/'native-hw-twi-completion'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 print('TWI completion:66624 cases;actual pinned CMSIS state query;asymmetric flags/fresh semaphore;36 imports;IRQ/ABI/kernel ownership/image gates open')
if __name__=='__main__':audit()
