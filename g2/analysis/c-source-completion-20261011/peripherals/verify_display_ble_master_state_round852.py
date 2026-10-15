#!/usr/bin/env python3
"""Check source-owned central-profile cell ABI and trial relocation imports."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[3]
build=root/'build/c-firmware/root-main-lvgl-label-providers-round814'
obj=build/'round852-master-state-cells.o'
trial=build/'candidate-ble-master-state-round852.o'
syms={}
for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(obj)],text=True).splitlines():
 fields=line.split()
 if len(fields)==4 and fields[-1].startswith('audio_ble_master_'):
  syms[fields[-1]]=(int(fields[0],16),int(fields[1],16),fields[2])
expected={'connect_wait':2,'auth_mode':1,'failure_notify':1,'failure_count':1,
 'connection_flag':1,'connect_state':1,'publish_flag':1,'link_ready':1,
 'context':4,'state_slot':4,'mode_slot':4,'state_shadow':4,'payload_slot':4,
 'registration_slot':4}
for short,size in expected.items():
 key='audio_ble_master_'+short
 assert key in syms and syms[key][1]==size,(key,syms.get(key))
assert syms['audio_ble_master_context'][0]==syms['audio_ble_master_state_slot'][0]
imports=subprocess.check_output(['arm-none-eabi-nm','-u',str(trial)],text=True).splitlines()
assert len(imports)==568,len(imports)
for short in expected:
 assert not any(line.endswith('audio_ble_master_'+short) for line in imports),short
print('PASS_DISPLAY_BLE_MASTER_STATE_ABI',len(expected),'cells,',len(imports),'remaining imports')
