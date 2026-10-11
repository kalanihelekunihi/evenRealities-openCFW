"""Bounded actual ARM compiled-C/native Cordio ATT callback comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_att_callbacks.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_att_runtime[128];
uint8_t *audio_ble_att_ccb_by_conn_id(uint8_t c){(void)c;return (uint8_t*)0x20002000;}
void g2_wsf_candidate_buffer_free_word(uint32_t p){(void)p;}
'''
def w(u,a,v):u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_att_dm_conn_callback_4b4e50',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for scenario in ('data_server','data_client','control_on','control_off','dm_open','dm_close'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x300000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   runtime=syms['audio_ble_att_runtime'] if compiled else 0x200610ac
   w(u,runtime+0x3c,0x20003000);w(u,runtime+0x40,0x20003040)
   for base,offset in ((0x20003000,0),(0x20003040,4)):
    for field in (0,4,12):w(u,base+field,0x300001+offset+field)
   w(u,runtime+0x50,0x300101);w(u,runtime+0x5c,0x300111)
   event=0x20004000;u.mem_write(event,bytes(16));u.mem_write(event,b'\x02')
   if scenario=='data_server':u.mem_write(event+8,b'\x01')
   if scenario=='control_on':u.mem_write(event+2,b'\x01')
   if scenario=='dm_open':u.mem_write(event+2,b'\x27');u.mem_write(event+6,b'\x34\x12')
   if scenario=='dm_close':u.mem_write(event+2,b'\x28')
   u.mem_write(0x2000200e,b'\x02')
   if scenario=='dm_close':w(u,0x20002010,0x20005000)
   u.reg_write(UC_ARM_REG_R0,2 if scenario.startswith('data') else event)
   u.reg_write(UC_ARM_REG_R1,3);u.reg_write(UC_ARM_REG_R2,event)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   child=(syms['audio_ble_att_ccb_by_conn_id']&~1 if compiled else 0x4b4eee)
   free=(syms['g2_wsf_candidate_buffer_free_word']&~1 if compiled else 0x5304d4)
   calls=[]
   def hook(uc,a,size,_):
    if a==child:res=0x20002000;calls.append(('ccb',uc.reg_read(UC_ARM_REG_R0)))
    elif a==free:res=0;calls.append(('free',uc.reg_read(UC_ARM_REG_R0)))
    elif 0x300000<=a<0x300200:
     calls.append(('callback',a,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));res=0
    else:return
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   start=(syms[{'data_server':'audio_ble_att_l2c_data_callback_4b4de0','data_client':'audio_ble_att_l2c_data_callback_4b4de0','control_on':'audio_ble_att_l2c_control_callback_4b4e08','control_off':'audio_ble_att_l2c_control_callback_4b4e08','dm_open':'audio_ble_att_dm_conn_callback_4b4e50','dm_close':'audio_ble_att_dm_conn_callback_4b4e50'}[scenario]] if compiled else {'data_server':0x4b4de0,'data_client':0x4b4de0,'control_on':0x4b4e08,'control_off':0x4b4e08,'dm_open':0x4b4e50,'dm_close':0x4b4e50}[scenario])|1
   u.emu_start(start,0x600000,count=2000)
   rows.append((calls,bytes(u.mem_read(0x20002000,20))))
  assert rows[0]==rows[1],(scenario,rows)
  print('PASS',scenario,len(rows[0][0]))
