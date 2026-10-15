#!/usr/bin/env python3
"""Verify source-owned Apollo Ambiq RAM cells and LV array header layout."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/ambiq_state.c'
candidate=root/'build/c-firmware/root-main-uled-option-fifteen-ambiq-state-integration-round798/candidate.o'
names=('audio_uart_ambiq_unit_cell','audio_uart_ambiq_vector_current_path_200746c4',
 'audio_uart_ambiq_vector_path_segments_20073cc0','audio_uart_ambiq_vector_path_data_20073cd4')
def table(path):
 lines=subprocess.check_output(['arm-none-eabi-nm','-S','--defined-only',str(path)],text=True).splitlines()
 return {p[3]:(int(p[0],16),int(p[1],16),p[2]) for line in lines if len(p:=line.split())==4}
with tempfile.TemporaryDirectory() as d:
 object_path=Path(d)/'state.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
  '-std=c11','-ffreestanding','-fno-builtin','-O2','-c',str(source),'-o',str(object_path)],check=True)
 for path in (object_path,candidate):
  symbols=table(path)
  for name,size in zip(names,(4,4,20,20)):
   assert symbols[name][1:]==(size,'B'),(path,name,symbols[name])
  assert symbols[names[1]][0]-symbols[names[0]][0]==4,path
  assert symbols[names[3]][0]-symbols[names[2]][0]==20,path
print('PASS_AMBIQ_STATE_LAYOUT',len(names),2)
