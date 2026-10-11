#!/usr/bin/env python3
"""Verify attributed sensor-context fields and their native ROM descriptor bounds."""
from pathlib import Path
import hashlib,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OUT=ROOT/'g2/build/touch-reset-sensor-contexts-20261011';OUT.mkdir(exist_ok=True)
src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_sensor_contexts.c'
obj=OUT/'sensors.o';data=OUT/'sensors.bin'
subprocess.run(['clang','-target','armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-objcopy','--dump-section','.touch_init.sensor_contexts='+str(data),str(obj)],check=True)
fw=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';blob=fw.read_bytes();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
expected=blob[32+0xb6c8-0x3300:32+0xb6c8-0x3300+90]
assert len(data.read_bytes())==90 and data.read_bytes()==expected
rows=[]
for i,pointer,count in [(0,0x200005fc,4),(1,0x20000624,4),(2,0x2000064c,1)]:
 offset=32+0xb0f8+144*i-0x3300
 assert struct.unpack_from('<I',blob,offset+4)[0]==pointer
 assert struct.unpack_from('<H',blob,offset+56)[0]==count
 rows.append({'widget':i,'sensor_pointer':hex(pointer),'sensor_count':count})
receipt={'status':'PASS_TYPED_RESET_SENSOR_CONTEXTS_90_BYTES','firmware_sha256':sha(fw),'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'object_sha256':sha(obj),'data_sha256':sha(data),'ram':'0x200005fc','rom':'0xb6c8','bytes':90,'widget_descriptor_checks':rows,'aggregate_source_owned_reset_bytes':403,'remaining_reset_bytes':561,'limits':['Initialized data and descriptor bounds only; final linker/pointer ownership and hardware tuning remain open.','LP historic buffer allocation extent is not established merely by observing zero bytes.']}
(HERE/'reset-sensor-context-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
