"""Actual ARM compiled-C versus native HCI ACL reassembly bounded branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRCS=[ROOT/'components/audio/uart_thread_source_candidate'/n for n in ('display_ble_hci_acl_reassemble.c','display_ble_hci_acl_children.c')]
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_controller_state_20071478[0xb0];
void *audio_wsf_msg_alloc(uint16_t n){(void)n;return 0;}
void audio_ble_wsf_message_free(void *p){(void)p;}
void __aeabi_memcpy(void *d,const void *s,unsigned n){uint8_t *a=d;const uint8_t *b=s;for(unsigned i=0;i<n;i++)a[i]=b[i];}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_acl_reassemble',*[str(x) for x in SRCS],str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,header,length,conn,payload in (('unknown',0x2002,4,False,4),('complete',0x2002,8,True,4),('zero',0x2002,0,True,4),('other',0x3002,4,True,4),('partial',0x2002,6,True,12),('continuation_complete',0x1002,4,True,4),('continuation_short',0x1002,4,True,4)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_controller_state_20071478'] if is_c else 0x20071478
   u.mem_write(state,b'\x00'*0xb0);u.mem_write(state+0x10,struct.pack('<H',2 if conn else 0xffff));u.mem_write(state+0x7c,struct.pack('<H',64))
   if name.startswith('continuation'):
    u.mem_write(state+8,struct.pack('<II',0x20006000,0x20006008))
    u.mem_write(state+0x14,struct.pack('<H',4 if name.endswith('complete') else 2))
   packet=0x20005000;data=bytearray(32);struct.pack_into('<HH',data,0,header,length);struct.pack_into('<H',data,4,payload);u.mem_write(packet,bytes(data))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,packet)
   calls=[];free=(syms['audio_ble_wsf_message_free']&~1) if is_c else 0x4bf9b0
   alloc=(syms['audio_wsf_msg_alloc']&~1) if is_c else 0x4bf990
   def hook(uc,a,size,_):
    if a==free:
     calls.append(('free',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif a==alloc:
     calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x20006000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif not is_c and a==0x439be4:
     dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2);uc.mem_write(dst,bytes(uc.mem_read(src,n)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_acl_reassemble'] if is_c else 0x52a962)|1,0x600000,count=900)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(state,0x80)),bytes(u.mem_read(0x20006000,24))))
  assert results[0]==results[1],(name,results[0][:2],results[1][:2])
  print('PASS',name,results[0][0],len(results[0][1]))
