#!/usr/bin/env python3
"""Audit persisted composition proof without loading emulator/test drivers."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-chain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 v=json.loads((OUT/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in v['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(OUT/'proof.elf')==v['proof_elf_sha256'] and sha(OUT/'proof.ld')==v['proof_layout_sha256'] and sha(ROOT/'r1/tools/verify_native_health_get_chain.py')==v['driver_sha256']
 assert v['workflows']==1296 and v['counts']=={'workflows':1296,'response':544,'flag':480,'invalid_handle':272,'offset':816} and v['trace_sha256']=='09c7878635afb389c011e123bb16a0f5a33347a9053841c222b94aa1632bd4bf'
 assert len(v['exact_spans'])==12 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==1054
 with tempfile.TemporaryDirectory() as t:
  for i,x in enumerate(v['exact_spans']):
   a=int(x['address'],16);native=raw[a-0x27000:a-0x27000+x['size']];assert hashlib.sha256(native).hexdigest()==x['sha256'];sec='templates' if i==11 else 'b'+str(i);f=Path(t)/'section.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(OUT/'proof.elf'),str(f)],check=True);assert f.read_bytes()==native
  for m,size in [(0,84),(1,84),(5,160)]:
   f=Path(t)/'cache.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.cache'+str(m),'-O','binary',str(OUT/'proof.elf'),str(f)],check=True);assert f.read_bytes()==bytes(size)
 syms={cols[2]:int(cols[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(OUT/'proof.elf')],text=True).splitlines() if len(cols:=line.split())==3}
 for fam,a in [('hr',0x2001654c),('spo2',0x200165a0),('hrv',0x200169c0)]:assert syms['r1_cache_'+fam]==syms['r1_health_storage_'+fam+'_prefix']==a
 assert v['shared_cache_bytes']==328 and v['actual_dispatcher_getters_encoders_and_sender_execute'] and v['independent_packet_header_and_result_oracle'] and v['time_offset_phone_log_flag_and_response_providers_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Health get chain:1296 workflows;1054 exact ROM bytes;328 existing cache bytes;time/transport/layout/image gates open')
if __name__=='__main__':audit()
