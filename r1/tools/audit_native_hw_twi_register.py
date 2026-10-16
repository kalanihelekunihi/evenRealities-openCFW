#!/usr/bin/env python3
"""Authenticate native register policy and unchanged compiled SDK dependency."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-hw-twi-register-runtime';rp=out/'report.json';b=json.loads(rp.read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==30720 and r['counts']==dict(read0=7680,read1=7680,write0=7680,write1=7680) and r['observation_counts']==dict(tx=32640,rx=1536,wait=11264,log=7680,write80_saved_r4=1920) and r['trace_sha256']=='5937663fe1609f3ce3d697106ae3f0852b08b72e845749f9139769eeffe3c86a'
 for flag in ['actual_four_product_adapters','only_nrfx_wait_error_are_fixtures','external_read_register_frame_and_saved_r2_r3_checked','write80_saved_r4_overwrite_preserved','read_length_width_and_timeout_asymmetry_checked','write_retry17_and_full_error_status_checked','retry_uses_original_copied_buffer_with_mutations','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['all_address_fullwords_verified','unbounded_retry_termination_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','sdk_hardware_transfer_verified','hardware_write_executed','instruction_identity','whole_image_complete']:assert not r[flag]
 assert sha(ROOT/'r1/tools/verify_native_hw_twi_register.py')==r['driver_sha256'] and sha(rp)==r['report_sha256'] and sha(out/'hw-register-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/source-config/runtime/native_hw_twi_register_verification.ld')==r['layout_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['objects','provider_reports']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert sha(out/'native-hw-twi-register-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-hw-twi-register-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==36
 assert sha(out/'twim-source.o')==b['sdk_object_sha256'] and undefined_symbols(out/'twim-source.o')[0]==[] and undefined_symbols(out/'hw-register-source.o')[0]==b['graph_undefined_symbols']
 assert b['sdk_source_unchanged'] and not b['sdk_hardware_transfer_verified'] and not b['sdk_control_block_native_identity_verified'] and b['closed_parent_imports']==[] and b['newly_exposed_imports']==[]
 sdk=json.loads((BASE/'sdk-twim/report.json').read_text());unit=sdk['units'][0];assert unit['source']=='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/drivers/src/nrfx_twim.c' and {'nrfx_twim_tx','nrfx_twim_rx','nrfx_twim_xfer'}<=set(unit['defined']) and unit['undefined']==[] and sha(BASE/'sdk-twim/nrfx_twim.o')==unit['object_sha256']
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as z:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,h in sdk['inputs'].items():
   assert sha(ROOT/p)==h,p
   if p.startswith(prefix):assert hashlib.sha256(z.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for a,n in [('54ff8',100),('5505c',100),('550c0',96),('55120',96)]:
  q=json.loads((BASE/'native-hw-twi-register'/('rea-bytes-'+a+'.json')).read_text())['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['provider']['id']=='ghidra' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 print('TWI register adapters:30720 cases;write80 saved-r4 overwrite retained;unchanged pinned TWIM compiles;36 imports;SDK/frame/ABI/image gates remain')
if __name__=='__main__':audit()
