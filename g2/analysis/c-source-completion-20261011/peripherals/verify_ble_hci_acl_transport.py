"""Actual compiled ARM C/native ACL transport and live record selection."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_acl_transport.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xc0];
uint32_t audio_ble_hci_driver_write(uint32_t t,uint16_t n,const void*p){(void)t;(void)n;(void)p;return n;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_get_buf_size',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 funcs={'size':(0x530d34,'audio_ble_hci_get_buf_size'),'next':(0x52a72e,'audio_ble_hci_next_conn_fragment'),'send':(0x52a76c,'audio_ble_hci_send_acl_data'),'transport':(0x53013c,'audio_ble_hci_transport_send_acl')}
 for label,fn,idx,credit,result in [('size','size',0,0,1),('none','next',-1,0,1),('last','next',2,0,1),('send_ok','send',0,2,1),('send_fail','send',0,2,0),('transport_ok','transport',0,0,1),('transport_fail','transport',0,0,0)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   data=bytearray(0xc0);struct.pack_into('<H',data,0x7e,5);data[0x82]=credit
   for i in range(3):struct.pack_into('<H',data,i*0x1c+0x10,0xffff)
   if idx>=0:struct.pack_into('<H',data,idx*0x1c+0x10,0x1234);data[idx*0x1c+0x16]=1
   u.mem_write(state,bytes(data));packet=0x20006000;u.mem_write(packet,struct.pack('<HH',0x1234,7)+bytes(20))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,state)
   u.reg_write(UC_ARM_REG_R1,packet)
   calls=[];cuts={0x4b4a02:'driver'} if not is_c else {syms['audio_ble_hci_driver_write']&~1:'driver'}
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    value=(1 if result else 0) if name=='child' else (uc.reg_read(UC_ARM_REG_R1) if result else 0)
    uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms[funcs[fn][1]] if is_c else funcs[fn][0])|1
   u.emu_start(entry,0x600000,count=350)
   ret=u.reg_read(UC_ARM_REG_R0)
   if fn=='next':ret=(ret-state)&0xffffffff if ret else 0
   rows.append((ret,calls,bytes(u.mem_read(state,0x83))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0])
