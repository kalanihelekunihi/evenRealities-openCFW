#!/usr/bin/env python3
"""Audit native CASE CRT compressed initializer extent without copying data."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
source=blob[0xd95c:0xd95c+0x68]
assert len(source)==104
out=bytearray();i=0;records=[]
while len(out)<0x1a4:
 start=i;destination=len(out);header=source[i];i+=1
 copy=header&15;clear=header>>4
 if copy==0:copy=source[i];i+=1
 if clear==0:clear=source[i];i+=1
 copy_bytes=copy-1;clear_bytes=clear-1
 out+=source[i:i+copy_bytes];i+=copy_bytes
 out+=bytes(clear_bytes)
 records.append({'source_offset':start,'destination_offset':destination,'literal_bytes':copy_bytes,'zero_bytes':clear_bytes})
assert i==104 and len(out)==0x1a4 and len(records)==18
runs=[];start=None
for index,value in enumerate(out):
 if value!=0 and start is None:start=index
 if value==0 and start is not None:runs.append([start,index]);start=None
if start is not None:runs.append([start,len(out)])
report={'source_image':'g2/blobs/official/g2-2.2.6.10/firmware_box.bin (payload after 32-byte header)',
 'compressed_address':'0x0800d95c','compressed_extent_bytes':104,'compressed_sha256':hashlib.sha256(source).hexdigest(),
 'destination_address':'0x20000000','destination_extent_bytes':len(out),'decoded_sha256':hashlib.sha256(out).hexdigest(),
 'record_count':len(records),'records':records,'nonzero_runs_offsets':runs,
 'typed_fields':[{'ram_offset':'0x124','width_bytes':4,'initial_value':int.from_bytes(out[0x124:0x128],'little'),'meaning':'initial system clock in hertz','consumer_examples':['0x08008420 SysTick','0x08004480 console timing','0x08004f14 clock plan']},
  {'ram_offset':'0x19c','width_bytes':4,'initial_value_hex':f'0x{int.from_bytes(out[0x19c:0x1a0],"little"):08x}','meaning':'scheduler depth/magic initial word; scheduler start later clears it','consumer_examples':['0x0800b31c task return','0x0800c57c scheduler start']}],
 'typed_consumers':[{'ram_offset':'0x2a','extent_bytes':80,'native_read_compare':'0x08009f80','native_write_repair':'0x08009e0c','register_selector':'16 + byte index','register_identity':'Cellwise CW221X battery fuel-gauge profile, independently matched by chip ID 0xA0, profile extent 0x10..0x5f, mode register 0x08, update flag register 0x0b and ready register 0xa7','independent_reference':'https://github.com/rockchip-linux/kernel/blob/develop-6.1/drivers/power/supply/cw221x_battery.c','product_value_provenance':'stock CASE only; independent battery characterization/profile source still missing','nonzero_values':sum(v!=0 for v in out[0x2a:0x7a]),'table_sha256':hashlib.sha256(out[0x2a:0x7a]).hexdigest()}],
 'contract':'Audit only. Exact typed field meanings, independent data source, final placement and full native data inventory are unresolved; no bytes are emitted as firmware source.'}
(HERE/'case-crt-data-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('compressed_sha256','decoded_sha256','record_count','nonzero_runs_offsets')},indent=2))
