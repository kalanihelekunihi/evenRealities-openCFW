#!/usr/bin/env python3
"""Audit the actual-C-memcmp record composition and explicit call relocation."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-record-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 v=json.loads((OUT/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in v['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(OUT/'proof.elf')==v['proof_elf_sha256'] and sha(OUT/'proof.ld')==v['proof_layout_sha256'] and sha(ROOT/'r1/tools/verify_native_record_chain.py')==v['driver_sha256']
 assert v['workflows']==19776 and v['counts']=={'workflows':19776,'memcmp':15552,'read':15072,'write':15072,'reinitialize':4128} and v['trace_sha256']=='1afd69399383bac09f32b200654e87427fab4aebd26591b8b2ea51a3d896d619'
 assert len(v['source_spans'])==4 and sum(x['size'] for x in v['source_spans'])==v['native_span_bytes']==412 and v['relocated_call_address']=='0x6c68a'
 differences=[]
 with tempfile.TemporaryDirectory() as temp:
  for i,x in enumerate(v['source_spans']):
   a=int(x['address'],16);native=raw[a-0x27000:a-0x27000+x['size']];assert hashlib.sha256(native).hexdigest()==x['native_sha256'];f=Path(temp)/'body.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(OUT/'proof.elf'),str(f)],check=True);source=f.read_bytes();assert len(source)==len(native) and sha(f)==x['source_sha256'];differences += [hex(a+j) for j,(n,s) in enumerate(zip(native,source)) if n!=s]
  assert differences==v['differing_byte_addresses']==['0x6c68a','0x6c68b','0x6c68c','0x6c68d']
  f=Path(temp)/'memcmp.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.memcmp','-O','binary',str(OUT/'proof.elf'),str(f)],check=True);assert len(f.read_bytes())==v['source_c_memcmp_text_bytes']==28 and sha(f)==v['memcmp_text_sha256']=='eb9419476a14e056dd6ae342809d77b2af7bb40c23c8655ca3e769942ea886e2'
 assert v['actual_validator_wrapper_persist_apply_and_c_memcmp_execute'] and v['independent_validation_packet_and_threshold_oracle'] and v['kv_mode_log_and_reinitialize_providers_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Record chain:19776 workflows;412 native-span bytes with4 explicit call-relocation bytes;28-byte C memcmp;KV/reinitialize/layout/image gates open')
if __name__=='__main__':audit()
