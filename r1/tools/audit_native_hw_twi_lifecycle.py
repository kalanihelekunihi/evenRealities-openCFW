#!/usr/bin/env python3
"""Authenticate lifecycle policy/config and a single upstream TWIM family."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from audit_source_frontier import section_bytes
 out=BASE/'native-hw-twi-lifecycle-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==7200 and r['counts']==dict(open=2400,close=2400,workflow=2400) and r['observation_counts']==dict(gpio=4000,init=4000,error=3000,enable=4000,disable=6400,uninit=6400,power_zero=6400,power_one=6400) and r['trace_sha256']=='22ecbf380072e9b238742b93b0d47ff85c6bdec6a61eef4052cca51d2b16fd7b'
 for flag in ['actual_lifecycle_and_power_register_sequence','only_sdk_gpio_error_are_fixtures','native_config_pointer_and_full16_bytes_checked','fresh_pin_irq_and_opened_after_lower_calls_checked','init_errors_log_and_continue_checked','repeated_lifecycle_workflows_checked','raw_r0_callee_sp_nonstack_ram_mmio_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['full_raw_abi_verified','cross_call_private_frame_history_verified','sdk_hardware_initialization_verified','metadata_operation_abi_migrated','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_hw_twi_lifecycle.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'hw-lifecycle-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_hw_twi_lifecycle_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-hw-twi-lifecycle-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-hw-twi-lifecycle-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==28
 assert not any(n.startswith('r1_hw_twi') for n in b['undefined_symbols'])
 assert sha(out/'twim-legacy-consolidated-source.o')==b['sdk_object_sha256'] and undefined_symbols(out/'twim-legacy-consolidated-source.o')[0]==[] and undefined_symbols(out/'hw-lifecycle-source.o')[0]==b['graph_undefined_symbols']
 assert b['single_twim_family_from_pre_twim_parent'] and b['legacy_sdk_source_unchanged'] and not b['sdk_control_block_native_identity_verified'] and not b['sdk_hardware_transfer_verified'] and b['closed_parent_imports']==['r1_hw_twi0_close','r1_hw_twi0_open','r1_hw_twi1_close','r1_hw_twi1_open'] and b['newly_exposed_imports']==[]
 assert b['composition_roles']['base']=='native-hw-twi-wait-runtime/native-hw-twi-wait-runtime.o' and not({'nrfx_twim_tx','nrfx_twim_rx','nrfx_twim_init','nrf_drv_twi_init'}&set(undefined_symbols(BASE/b['composition_roles']['base'])[1]))
 nm=[x.split() for x in subprocess.check_output(['arm-none-eabi-nm','-S',str(out/'twim-legacy-consolidated-source.o')],text=True).splitlines()]
 for n,size in [('m_cb',104),('m_contexts',8),('m_handlers',8)]:
  rows=[x for x in nm if x[-1:]==[n]];assert len(rows)==1 and int(rows[0][1],16)==size and rows[0][2]=='b'
 sdk=json.loads((BASE/'sdk-legacy-twi/report.json').read_text());assert sdk['units'][0]['source']=='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/integration/nrfx/legacy/nrf_drv_twi.c' and sdk['units'][0]['object_sha256']==sha(BASE/'sdk-legacy-twi/nrf_drv_twi.o')
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,h in sdk['inputs'].items():
   assert sha(ROOT/p)==h,p
   if p.startswith(prefix):assert hashlib.sha256(z.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('55180',52),('551b4',52),('55278',108),('552e4',76),('9a600',8),('9a620',8)]:
  q=json.loads((BASE/'native-hw-twi-lifecycle'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for section,a in [('template0',0x9a600),('template1',0x9a620)]:assert section_bytes(BASE/'native-hw-twi-lifecycle/native_hw_twi_lifecycle.o','.r1.hw_twi.'+section,executable=False)==raw[a-0x27000:a-0x27000+8]
 for p,h in json.loads((out/'superseded-evidence.json').read_text()).items():assert sha(out/p)==h,p
 print('TWI lifecycle:7200 cases;16 exact template bytes;single upstream SDK state family;all TWI imports source-linked;28 remain;hardware/ABI/image gates open')
if __name__=='__main__':audit()
